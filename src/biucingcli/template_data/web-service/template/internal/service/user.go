package service

import (
	"{{MODULE_NAME}}/internal/model"
	"{{MODULE_NAME}}/internal/repository"
)

type UserService interface {
	ListUsers() []model.User
	GetUser(id string) (model.User, bool)
}

type userService struct {
	repository repository.UserRepository
}

func NewUserService(repository repository.UserRepository) UserService {
	return userService{repository: repository}
}

func (service userService) ListUsers() []model.User {
	return service.repository.List()
}

func (service userService) GetUser(id string) (model.User, bool) {
	return service.repository.GetByID(id)
}
