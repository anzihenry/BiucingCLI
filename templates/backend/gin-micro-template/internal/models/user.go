package models

import (
	"time"

	"gorm.io/gorm"
)

// User represents a user in the system.
type User struct {
	ID        uint           `gorm:"primaryKey" json:"id"`
	Username  string         `gorm:"size:255;uniqueIndex;not null" json:"username"`
	Email     string         `gorm:"size:255;uniqueIndex;not null" json:"email"`
	Password  string         `gorm:"size:255;not null" json:"-"`
	Profile   Profile        `gorm:"foreignKey:UserID" json:"profile,omitempty"`
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
}

// Profile represents a user profile.
type Profile struct {
	ID        uint           `gorm:"primaryKey" json:"id"`
	UserID    uint           `gorm:"uniqueIndex;not null" json:"user_id"`
	Bio       string         `gorm:"type:text" json:"bio"`
	Avatar    string         `gorm:"size:500" json:"avatar"`
	User      User           `gorm:"foreignKey:UserID" json:"-"`
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
}

// TableName specifies the table name for User.
func (User) TableName() string {
	return "users"
}

// TableName specifies the table name for Profile.
func (Profile) TableName() string {
	return "profiles"
}
