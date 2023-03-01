package main

import (
	"fmt"
	"context"
	"github.com/aws/aws-lambda-go/lambda"
)

type Request struct {
	prompt string `json:"prompt"`
	image string `json:"image"`
}

func HandleRequest(ctx context.Context, request Request) (string, error) {
	return fmt.Sprintf("Prompt %s, Image: ", request.prompt, request.image ), nil
}

func main() {
	lambda.Start(HandleRequest)
}