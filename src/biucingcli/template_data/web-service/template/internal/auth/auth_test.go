package auth

import (
	"context"
	"crypto/rand"
	"crypto/rsa"
	"encoding/json"
	"github.com/gin-gonic/gin"
	"github.com/go-jose/go-jose/v4"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"strings"
	"sync/atomic"
	"testing"
	"time"
	"{{MODULE_NAME}}/internal/database"
)

type fixture struct {
	server   *httptest.Server
	key      *rsa.PrivateKey
	online   atomic.Bool
	keys     atomic.Value
	nonce    string
	verifier string
}

func newFixture(t *testing.T) *fixture {
	t.Helper()
	key, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		t.Fatal(err)
	}
	f := &fixture{key: key}
	f.online.Store(true)
	f.keys.Store(jose.JSONWebKeySet{Keys: []jose.JSONWebKey{{Key: &key.PublicKey, KeyID: "one", Algorithm: "RS256", Use: "sig"}}})
	f.server = httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if !f.online.Load() {
			w.WriteHeader(503)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		if r.URL.Path == "/keys" {
			_ = json.NewEncoder(w).Encode(f.keys.Load())
			return
		}
		if r.URL.Path == "/token" {
			if err := r.ParseForm(); err != nil || r.Form.Get("code_verifier") != f.verifier || r.Form.Get("code") != "fixture-code" {
				w.WriteHeader(400)
				return
			}
			_ = json.NewEncoder(w).Encode(map[string]any{"access_token": "discarded", "token_type": "Bearer", "id_token": f.sign(t, "JWT", "web", f.server.URL, time.Now().Add(time.Hour), "one")})
			return
		}
		w.WriteHeader(404)
	}))
	t.Cleanup(f.server.Close)
	return f
}
func (f *fixture) sign(t *testing.T, typ, aud, issuer string, expires time.Time, kid string) string {
	t.Helper()
	signer, err := jose.NewSigner(jose.SigningKey{Algorithm: jose.RS256, Key: f.key}, (&jose.SignerOptions{}).WithType(jose.ContentType(typ)).WithHeader("kid", kid))
	if err != nil {
		t.Fatal(err)
	}
	claims, _ := json.Marshal(map[string]any{"iss": issuer, "sub": "person", "aud": aud, "exp": expires.Unix(), "iat": time.Now().Unix(), "nonce": f.nonce, "client_id": "mobile", "jti": "fixture-id"})
	signed, err := signer.Sign(claims)
	if err != nil {
		t.Fatal(err)
	}
	raw, err := signed.CompactSerialize()
	if err != nil {
		t.Fatal(err)
	}
	return raw
}
func (f *fixture) config() Config {
	return Config{Issuer: f.server.URL, JWKS: f.server.URL + "/keys", AuthorizeURL: f.server.URL + "/authorize", TokenURL: f.server.URL + "/token", ClientID: "web", Audience: "api", Origin: "https://app.example", Callback: "https://app.example/auth/callback", Secure: true}
}
func TestAccessTokenPurposeAndOutage(t *testing.T) {
	f := newFixture(t)
	s := New(context.Background(), f.config(), nil)
	future := time.Now().Add(time.Hour)
	good := f.sign(t, "at+jwt", "api", f.server.URL, future, "one")
	if _, err := s.Access(context.Background(), good); err != nil {
		t.Fatal(err)
	}
	for _, bad := range []string{f.sign(t, "JWT", "api", f.server.URL, future, "one"), f.sign(t, "at+jwt", "web", f.server.URL, future, "one"), f.sign(t, "at+jwt", "api", "https://unknown", future, "one"), f.sign(t, "at+jwt", "api", f.server.URL, time.Now().Add(-time.Minute), "one"), good + "bad"} {
		if _, err := s.Access(context.Background(), bad); err == nil {
			t.Fatal("accepted invalid token")
		}
	}
	f.online.Store(false)
	if _, err := s.Access(context.Background(), good); err != nil {
		t.Fatal("cached valid key failed during outage", err)
	}
	if _, err := s.Access(context.Background(), f.sign(t, "at+jwt", "api", f.server.URL, future, "unknown")); err == nil {
		t.Fatal("unknown key allowed")
	}
}
func TestPostgresBrowserFlow(t *testing.T) {
	dsn := os.Getenv("TEST_DATABASE_DSN")
	if dsn == "" {
		t.Skip("requires PostgreSQL")
	}
	store, err := database.Open(context.Background(), dsn, database.Config{MaxConnections: 4, QueryTimeoutSeconds: 3})
	if err != nil {
		t.Fatal(err)
	}
	defer store.Close()
	f := newFixture(t)
	service := New(context.Background(), f.config(), store)
	engine := gin.New()
	engine.Use(service.Middleware())
	service.Register(engine)
	login := httptest.NewRecorder()
	engine.ServeHTTP(login, httptest.NewRequest("GET", "/auth/login", nil))
	if login.Code != 302 {
		t.Fatal(login.Code, login.Body.String())
	}
	location, err := url.Parse(login.Header().Get("Location"))
	if err != nil {
		t.Fatal(err)
	}
	state := location.Query().Get("state")
	f.nonce = location.Query().Get("nonce")
	if err = store.Pool.QueryRow(context.Background(), "SELECT verifier FROM login_attempts WHERE state_hash=$1", hash(state)).Scan(&f.verifier); err != nil {
		t.Fatal(err)
	}
	callback := "/auth/callback?state=" + state + "&code=fixture-code"
	forged := httptest.NewRecorder()
	engine.ServeHTTP(forged, httptest.NewRequest("GET", callback, nil))
	if forged.Code != 401 {
		t.Fatal("missing browser binding accepted")
	}
	req := httptest.NewRequest("GET", callback, nil)
	req.AddCookie(login.Result().Cookies()[0])
	old := token()
	_, err = store.Pool.Exec(context.Background(), "INSERT INTO sessions(id_hash,issuer,subject,csrf,expires_at) VALUES($1,'old','old','old',now()+interval '1 hour')", hash(old))
	if err != nil {
		t.Fatal(err)
	}
	req.AddCookie(&http.Cookie{Name: "__Host-session", Value: old})
	response := httptest.NewRecorder()
	engine.ServeHTTP(response, req)
	if response.Code != 200 {
		t.Fatal(response.Code, response.Body.String())
	}
	var oldCount int
	if err = store.Pool.QueryRow(context.Background(), "SELECT count(*) FROM sessions WHERE id_hash=$1", hash(old)).Scan(&oldCount); err != nil || oldCount != 0 {
		t.Fatal("session not rotated", err)
	}
	var cookie *http.Cookie
	for _, c := range response.Result().Cookies() {
		if c.Name == "__Host-session" {
			cookie = c
		}
	}
	if cookie == nil || !cookie.Secure || !cookie.HttpOnly || cookie.Domain != "" {
		t.Fatal("unsafe cookie")
	}
	replay := httptest.NewRecorder()
	engine.ServeHTTP(replay, req)
	if replay.Code != 401 {
		t.Fatal("callback replay accepted")
	}
	// A second service instance shares the database; IdP outage does not extend expiry.
	second := New(context.Background(), f.config(), store)
	engine = gin.New()
	engine.Use(second.Middleware())
	second.Register(engine)
	f.online.Store(false)
	call := func(method, path, origin, csrf string) *httptest.ResponseRecorder {
		r := httptest.NewRequest(method, path, strings.NewReader(""))
		r.AddCookie(cookie)
		r.Header.Set("Origin", origin)
		r.Header.Set("X-CSRF-Token", csrf)
		w := httptest.NewRecorder()
		engine.ServeHTTP(w, r)
		return w
	}
	session := call("GET", "/auth/session", "", "")
	if session.Code != 200 {
		t.Fatal(session.Code)
	}
	var body map[string]string
	if err = json.Unmarshal(session.Body.Bytes(), &body); err != nil {
		t.Fatal(err)
	}
	for _, origin := range []string{"", "https://evil.example"} {
		if call("POST", "/auth/logout", origin, body["csrf_token"]).Code != 403 {
			t.Fatal("cross-site write accepted")
		}
	}
	if _, err = store.Pool.Exec(context.Background(), "UPDATE sessions SET expires_at=now()-interval '1 second' WHERE id_hash=$1", hash(cookie.Value)); err != nil {
		t.Fatal(err)
	}
	if call("GET", "/auth/session", "", "").Code != 401 {
		t.Fatal("expired session accepted")
	}
	if _, err = store.Pool.Exec(context.Background(), "UPDATE sessions SET expires_at=now()+interval '1 hour' WHERE id_hash=$1", hash(cookie.Value)); err != nil {
		t.Fatal(err)
	}
	if call("POST", "/auth/logout", "https://app.example", "wrong").Code != 403 {
		t.Fatal("missing CSRF accepted")
	}
	if call("POST", "/auth/logout", "https://app.example", body["csrf_token"]).Code != 204 {
		t.Fatal("logout failed")
	}
	if call("GET", "/auth/session", "", "").Code != 401 {
		t.Fatal("revoked session accepted")
	}
}

func TestJWKSKeyRollover(t *testing.T) {
	f := newFixture(t)
	s := New(context.Background(), f.config(), nil)
	future := time.Now().Add(time.Hour)
	if _, err := s.Access(context.Background(), f.sign(t, "at+jwt", "api", f.server.URL, future, "one")); err != nil {
		t.Fatal(err)
	}
	next, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		t.Fatal(err)
	}
	f.keys.Store(jose.JSONWebKeySet{Keys: []jose.JSONWebKey{{Key: &f.key.PublicKey, KeyID: "one", Algorithm: "RS256", Use: "sig"}, {Key: &next.PublicKey, KeyID: "two", Algorithm: "RS256", Use: "sig"}}})
	f.key = next
	raw := f.sign(t, "at+jwt", "api", f.server.URL, future, "two")
	if _, err = s.Access(context.Background(), raw); err != nil {
		t.Fatal("new key was not refreshed", err)
	}
	f.online.Store(false)
	if _, err = s.Access(context.Background(), raw); err != nil {
		t.Fatal("refreshed key not cached", err)
	}
}
