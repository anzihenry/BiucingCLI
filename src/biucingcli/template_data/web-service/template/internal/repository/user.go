package repository

import (
	"context"

	"{{MODULE_NAME}}/internal/model"
)

type UserRepository interface {
	List(ctx context.Context) ([]model.User, error)
	GetByID(ctx context.Context, id string) (model.User, bool, error)
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

func (repository inMemoryUserRepository) List(ctx context.Context) ([]model.User, error) {
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	users := make([]model.User, len(repository.users))
	copy(users, repository.users)
	return users, nil
}

func (repository inMemoryUserRepository) GetByID(ctx context.Context, id string) (model.User, bool, error) {
	if err := ctx.Err(); err != nil {
		return model.User{}, false, err
	}
	for _, user := range repository.users {
		if user.ID == id {
			return user, true, nil
		}
	}

	return model.User{}, false, nil
}
