package service

import (
	"context"

	"{{MODULE_NAME}}/internal/model"
	"{{MODULE_NAME}}/internal/repository"
)

type UserService interface {
	ListUsers(ctx context.Context) ([]model.User, error)
	GetUser(ctx context.Context, id string) (model.User, bool, error)
}

type userService struct {
	repository repository.UserRepository
}

func NewUserService(repository repository.UserRepository) UserService {
	return userService{repository: repository}
}

func (service userService) ListUsers(ctx context.Context) ([]model.User, error) {
	return service.repository.List(ctx)
}

func (service userService) GetUser(ctx context.Context, id string) (model.User, bool, error) {
	return service.repository.GetByID(ctx, id)
}
