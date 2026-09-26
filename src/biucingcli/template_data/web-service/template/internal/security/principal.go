package security

import "context"

type Principal struct {
	Subject  string
	Issuer   string
	Workload string
}
type principalKey struct{}

// Only credential verifiers may construct a principal; never trust inbound identity headers.
func WithPrincipal(ctx context.Context, p Principal) context.Context {
	return context.WithValue(ctx, principalKey{}, p)
}
func FromContext(ctx context.Context) (Principal, bool) {
	p, ok := ctx.Value(principalKey{}).(Principal)
	return p, ok
}

type Policy func(context.Context, Principal, string) bool

func Authorized(ctx context.Context, action string, policy Policy) bool {
	p, ok := FromContext(ctx)
	return ok && policy != nil && policy(ctx, p, action)
}
