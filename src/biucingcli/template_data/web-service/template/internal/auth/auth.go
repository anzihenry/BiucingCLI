package auth

import (
	"context"
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"errors"
	"github.com/coreos/go-oidc/v3/oidc"
	"github.com/gin-gonic/gin"
	"github.com/jackc/pgx/v5"
	"golang.org/x/oauth2"
	"net/http"
	"net/url"
	"strings"
	"time"
	"{{MODULE_NAME}}/internal/database"
	"{{MODULE_NAME}}/internal/security"
)

type Config struct {
	Issuer       string `yaml:"issuer"`
	JWKS         string `yaml:"jwks"`
	AuthorizeURL string `yaml:"authorize_url"`
	TokenURL     string `yaml:"token_url"`
	ClientID     string `yaml:"client_id"`
	ClientSecret string `yaml:"-"`
	Audience     string `yaml:"audience"`
	Origin       string `yaml:"origin"`
	Callback     string `yaml:"callback"`
	Secure       bool   `yaml:"secure"`
}

func (c Config) Validate(production bool) error {
	for _, s := range []string{c.Issuer, c.JWKS, c.AuthorizeURL, c.TokenURL, c.Origin, c.Callback} {
		u, e := url.Parse(s)
		if e != nil || u.Host == "" || u.User != nil || u.Fragment != "" || (u.Scheme != "https" && (production || u.Scheme != "http")) {
			return errors.New("invalid OIDC endpoint configuration")
		}
	}
	origin, e := url.Parse(c.Origin)
	if e != nil || origin.Path != "" || origin.RawQuery != "" {
		return errors.New("origin must be exact scheme and authority")
	}
	if c.Callback != c.Origin+"/auth/callback" || c.ClientID == "" || c.Audience == "" || c.ClientID == c.Audience || (production && (!c.Secure || c.ClientSecret == "" || c.ClientSecret == "local-web-secret")) {
		return errors.New("invalid OIDC client configuration")
	}
	return nil
}

type Service struct {
	config     Config
	store      *database.Store
	id, access *oidc.IDTokenVerifier
	oauth      oauth2.Config
}

func New(ctx context.Context, c Config, store *database.Store) *Service {
	client := &http.Client{Timeout: 4 * time.Second}
	ctx = oidc.ClientContext(ctx, client)
	keys := oidc.NewRemoteKeySet(ctx, c.JWKS)
	return &Service{c, store, oidc.NewVerifier(c.Issuer, keys, &oidc.Config{ClientID: c.ClientID, SupportedSigningAlgs: []string{"RS256"}}), oidc.NewVerifier(c.Issuer, keys, &oidc.Config{ClientID: c.Audience, SupportedSigningAlgs: []string{"RS256"}}), oauth2.Config{ClientID: c.ClientID, ClientSecret: c.ClientSecret, RedirectURL: c.Callback, Scopes: []string{oidc.ScopeOpenID}, Endpoint: oauth2.Endpoint{AuthURL: c.AuthorizeURL, TokenURL: c.TokenURL}}}
}
func token() string { return base64.RawURLEncoding.EncodeToString(random(32)) }
func random(n int) []byte {
	b := make([]byte, n)
	if _, e := rand.Read(b); e != nil {
		panic("random source unavailable")
	}
	return b
}
func hash(s string) string { sum := sha256.Sum256([]byte(s)); return hex.EncodeToString(sum[:]) }
func (s *Service) cookie(c *gin.Context, name, value string, age int) {
	http.SetCookie(c.Writer, &http.Cookie{Name: name, Value: value, Path: "/", MaxAge: age, Secure: s.config.Secure, HttpOnly: true, SameSite: http.SameSiteLaxMode})
}
func (s *Service) name() string {
	if s.config.Secure {
		return "__Host-session"
	}
	return "dev-session"
}
func (s *Service) loginName() string {
	if s.config.Secure {
		return "__Host-login"
	}
	return "dev-login"
}
func fail(c *gin.Context, code int) {
	c.AbortWithStatusJSON(code, gin.H{"error": "authentication_failed"})
}
func (s *Service) Register(e *gin.Engine) {
	e.GET("/auth/login", s.Login)
	e.GET("/auth/callback", s.Callback)
	e.GET("/auth/session", s.Session)
	e.POST("/auth/logout", s.Logout)
}
func (s *Service) Login(c *gin.Context) {
	// Fixed redirect only. Never accept return_to or caller-supplied callback URLs.
	state, nonce, verifier, binding := token(), token(), oauth2.GenerateVerifier(), token()
	ctx, stop := s.store.Context(c.Request.Context())
	defer stop()
	_, err := s.store.Pool.Exec(ctx, "INSERT INTO login_attempts(state_hash,binding_hash,nonce,verifier,expires_at) VALUES($1,$2,$3,$4,now()+interval '5 minutes')", hash(state), hash(binding), nonce, verifier)
	if err != nil {
		fail(c, 503)
		return
	}
	s.cookie(c, s.loginName(), binding, 300)
	c.Redirect(302, s.oauth.AuthCodeURL(state, oidc.Nonce(nonce), oauth2.S256ChallengeOption(verifier)))
}
func (s *Service) Callback(c *gin.Context) {
	state, code := c.Query("state"), c.Query("code")
	binding, err := c.Cookie(s.loginName())
	if err != nil || len(state) != 43 || len(binding) != 43 || code == "" || len(code) > 4096 {
		fail(c, 401)
		return
	}
	ctx, stop := s.store.Context(c.Request.Context())
	defer stop()
	var nonce, verifier string
	err = s.store.Pool.QueryRow(ctx, "DELETE FROM login_attempts WHERE state_hash=$1 AND binding_hash=$2 AND expires_at>now() RETURNING nonce,verifier", hash(state), hash(binding)).Scan(&nonce, &verifier)
	s.cookie(c, s.loginName(), "", -1)
	if err != nil {
		fail(c, 401)
		return
	}
	ctx = context.WithValue(ctx, oauth2.HTTPClient, &http.Client{Timeout: 4 * time.Second})
	exchanged, err := s.oauth.Exchange(ctx, code, oauth2.VerifierOption(verifier))
	if err != nil {
		fail(c, 401)
		return
	}
	raw, ok := exchanged.Extra("id_token").(string)
	if !ok {
		fail(c, 401)
		return
	}
	verified, err := s.id.Verify(ctx, raw)
	if err != nil || verified.Subject == "" || subtle.ConstantTimeCompare([]byte(verified.Nonce), []byte(nonce)) != 1 {
		fail(c, 401)
		return
	}
	var idClaims struct {
		AuthorizedParty string `json:"azp"`
	}
	if err = verified.Claims(&idClaims); err != nil || (len(verified.Audience) > 1 && idClaims.AuthorizedParty != s.config.ClientID) || (idClaims.AuthorizedParty != "" && idClaims.AuthorizedParty != s.config.ClientID) {
		fail(c, 401)
		return
	}
	// Retain no provider access/refresh/ID token. Session has an absolute deadline;
	// extending it requires a new complete authorization-code flow.
	id, csrf := token(), token()
	expires := time.Now().Add(time.Hour)
	if verified.Expiry.Before(expires) {
		expires = verified.Expiry
	}
	old, _ := c.Cookie(s.name())
	err = s.store.Within(ctx, func(ctx context.Context, tx pgx.Tx) error {
		if _, e := tx.Exec(ctx, "DELETE FROM sessions WHERE id_hash=$1", hash(old)); e != nil {
			return e
		}
		_, e := tx.Exec(ctx, "INSERT INTO sessions(id_hash,issuer,subject,csrf,expires_at) VALUES($1,$2,$3,$4,$5)", hash(id), verified.Issuer, verified.Subject, csrf, expires)
		return e
	})
	if err != nil {
		fail(c, 503)
		return
	}
	s.cookie(c, s.name(), id, int(time.Until(expires).Seconds()))
	c.Header("Cache-Control", "no-store")
	c.JSON(200, gin.H{"authenticated": true})
}
func (s *Service) Access(ctx context.Context, raw string) (security.Principal, error) {
	if len(raw) > 16384 {
		return security.Principal{}, errors.New("invalid access token")
	}
	parts := strings.Split(raw, ".")
	if len(parts) != 3 {
		return security.Principal{}, errors.New("invalid access token")
	}
	header, err := base64.RawURLEncoding.DecodeString(parts[0])
	if err != nil {
		return security.Principal{}, err
	}
	var h struct {
		Type string `json:"typ"`
	}
	if json.Unmarshal(header, &h) != nil || h.Type != "at+jwt" {
		return security.Principal{}, errors.New("access token purpose required")
	}
	verified, err := s.access.Verify(ctx, raw)
	if err != nil {
		return security.Principal{}, err
	}
	if verified.Subject == "" {
		return security.Principal{}, errors.New("subject required")
	}
	var claims struct {
		NotBefore int64  `json:"nbf"`
		ClientID  string `json:"client_id"`
		IssuedAt  int64  `json:"iat"`
		ID        string `json:"jti"`
	}
	if err = verified.Claims(&claims); err != nil || claims.NotBefore > time.Now().Unix() || claims.ClientID == "" || claims.IssuedAt <= 0 || claims.IssuedAt > time.Now().Unix()+30 || claims.ID == "" || len(claims.ID) > 256 {
		return security.Principal{}, errors.New("invalid access claims")
	}
	return security.Principal{Issuer: verified.Issuer, Subject: verified.Subject}, nil
}
func (s *Service) Middleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Request.Header.Del("X-User-Issuer")
		c.Request.Header.Del("X-User-Subject")
		c.Request.Header.Del("X-User-ID")
		origin := c.GetHeader("Origin")
		if origin != "" {
			if origin != s.config.Origin {
				fail(c, 403)
				return
			}
			c.Header("Access-Control-Allow-Origin", origin)
			c.Header("Access-Control-Allow-Credentials", "true")
			c.Header("Vary", "Origin")
			if c.Request.Method == "OPTIONS" {
				c.Header("Access-Control-Allow-Methods", "GET, POST")
				c.Header("Access-Control-Allow-Headers", "Content-Type, X-CSRF-Token, Authorization")
				c.AbortWithStatus(204)
				return
			}
		}
		if c.Request.URL.Path == "/auth/login" || c.Request.URL.Path == "/auth/callback" {
			return
		}
		authorization := c.GetHeader("Authorization")
		id, ce := c.Cookie(s.name())
		if authorization != "" {
			if ce == nil || !strings.HasPrefix(authorization, "Bearer ") {
				fail(c, 401)
				return
			}
			principal, err := s.Access(c.Request.Context(), strings.TrimPrefix(authorization, "Bearer "))
			if err != nil {
				fail(c, 401)
				return
			}
			c.Request = c.Request.WithContext(security.WithPrincipal(c.Request.Context(), principal))

			return
		}
		if ce == nil {
			if len(id) != 43 {
				fail(c, 401)
				return
			}
			ctx, stop := s.store.Context(c.Request.Context())
			defer stop()
			var p security.Principal
			var csrf string
			err := s.store.Pool.QueryRow(ctx, "SELECT issuer,subject,csrf FROM sessions WHERE id_hash=$1 AND expires_at>now()", hash(id)).Scan(&p.Issuer, &p.Subject, &csrf)
			if err != nil {
				if errors.Is(err, pgx.ErrNoRows) {
					fail(c, 401)
				} else {
					fail(c, 503)
				}
				return
			}
			if c.Request.Method != "GET" && c.Request.Method != "HEAD" && (origin != s.config.Origin || subtle.ConstantTimeCompare([]byte(c.GetHeader("X-CSRF-Token")), []byte(csrf)) != 1) {
				fail(c, 403)
				return
			}
			c.Set("csrf", csrf)
			c.Request = c.Request.WithContext(security.WithPrincipal(c.Request.Context(), p))
		}

	}
}
func (s *Service) Session(c *gin.Context) {
	p, ok := security.FromContext(c.Request.Context())
	if !ok {
		fail(c, 401)
		return
	}
	c.Header("Cache-Control", "no-store")
	c.JSON(200, gin.H{"issuer": p.Issuer, "subject": p.Subject, "csrf_token": c.GetString("csrf")})
}
func (s *Service) Logout(c *gin.Context) {
	id, _ := c.Cookie(s.name())
	ctx, stop := s.store.Context(c.Request.Context())
	defer stop()
	if _, err := s.store.Pool.Exec(ctx, "DELETE FROM sessions WHERE id_hash=$1", hash(id)); err != nil {
		fail(c, 503)
		return
	}
	s.cookie(c, s.name(), "", -1)
	c.Status(204)
}
