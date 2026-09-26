package pipeline

import (
	"encoding/json"
	"errors"
	"io"
)

// Call after the size-limited HTTP middleware. Reject unknown fields and extra documents.
func DecodeJSON(body io.Reader, target any) error {
	decoder := json.NewDecoder(body)
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(target); err != nil {
		return errors.New("invalid JSON")
	}
	var extra any
	if err := decoder.Decode(&extra); err != io.EOF {
		return errors.New("expected one JSON document")
	}
	if validator, ok := target.(interface{ Validate() error }); ok && validator.Validate() != nil {
		return errors.New("invalid request")
	}
	return nil
}
