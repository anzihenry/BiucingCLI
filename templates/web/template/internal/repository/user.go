package repository

import "{{MODULE_NAME}}/internal/model"

type UserRepository interface {
	List() []model.User
	GetByID(id string) (model.User, bool)
}

type inMemoryUserRepository struct {
	users []model.User
}

func NewUserRepository() UserRepository {
	return inMemoryUserRepository{
		users: []model.User{
			{ID: "u_001", Name: "Ada Lovelace", Email: "ada@example.com"},
			{ID: "u_002", Name: "Alan Turing", Email: "alan@example.com"},
		},
	}
}

func (repository inMemoryUserRepository) List() []model.User {
	users := make([]model.User, len(repository.users))
	copy(users, repository.users)
	return users
}

func (repository inMemoryUserRepository) GetByID(id string) (model.User, bool) {
	for _, user := range repository.users {
		if user.ID == id {
			return user, true
		}
	}

	return model.User{}, false
}
