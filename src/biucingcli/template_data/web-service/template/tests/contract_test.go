package tests

import (
	"context"
	"github.com/getkin/kin-openapi/openapi3"
	"github.com/getkin/kin-openapi/openapi3filter"
	"github.com/getkin/kin-openapi/routers/legacy"
	"net/http/httptest"
	"testing"
	"{{MODULE_NAME}}/api"
	"{{MODULE_NAME}}/internal/config"
	"{{MODULE_NAME}}/internal/router"
)

func TestHTTPContract(t *testing.T) {
	data, err := api.Contract.ReadFile("openapi.json")
	if err != nil {
		t.Fatal(err)
	}
	spec, err := openapi3.NewLoader().LoadFromData(data)
	if err != nil {
		t.Fatal(err)
	}
	if err = spec.Validate(context.Background()); err != nil {
		t.Fatal(err)
	}
	routes, err := legacy.NewRouter(spec)
	if err != nil {
		t.Fatal(err)
	}
	for _, path := range []string{"/api/v1/ping", "/auth/session"} {
		req := httptest.NewRequest("GET", path, nil)
		rec := httptest.NewRecorder()
		router.New(config.Config{}).ServeHTTP(rec, req)
		route, params, err := routes.FindRoute(req)
		if err != nil {
			t.Fatal(err)
		}
		input := &openapi3filter.RequestValidationInput{Request: req, PathParams: params, Route: route}
		output := &openapi3filter.ResponseValidationInput{RequestValidationInput: input, Status: rec.Code, Header: rec.Header(), Options: &openapi3filter.Options{IncludeResponseStatus: true}}
		output.SetBodyBytes(rec.Body.Bytes())
		if err = openapi3filter.ValidateResponse(context.Background(), output); err != nil {
			t.Fatal(err)
		}
	}
}
