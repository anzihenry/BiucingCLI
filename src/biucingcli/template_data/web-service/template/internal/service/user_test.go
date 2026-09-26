package service

import (
	"context"
	"errors"
	"testing"

	"{{MODULE_NAME}}/internal/model"
)

type contextCheckingRepository struct {
	contextKey any
}

func (repository contextCheckingRepository) List(ctx context.Context) ([]model.User, error) {
	if ctx.Value(repository.contextKey) != "request-value" {
		return nil, errors.New("request context was not propagated")
	}
	return []model.User{{ID: "u_001"}}, nil
}

func (repository contextCheckingRepository) GetByID(ctx context.Context, id string) (model.User, bool, error) {
	if ctx.Value(repository.contextKey) != "request-value" {
		return model.User{}, false, errors.New("request context was not propagated")
	}
	return model.User{ID: id}, true, nil
}

func TestUserServicePropagatesRequestContext(t *testing.T) {
	key := new(int)
	ctx := context.WithValue(context.Background(), key, "request-value")
	service := NewUserService(contextCheckingRepository{contextKey: key})
	users, err := service.ListUsers(ctx)
	if err != nil || len(users) != 1 {
		t.Fatalf("list users: %v, %v", users, err)
	}
	user, found, err := service.GetUser(ctx, "u_002")
	if err != nil || !found || user.ID != "u_002" {
		t.Fatalf("get user: %v, %v, %v", user, found, err)
	}
}
