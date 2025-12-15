FROM golang:1.21-alpine AS builder

RUN apk add --no-cache git zeromq-dev build-base

WORKDIR /app

COPY go.mod ./
COPY main.go ./

RUN go mod download && go mod tidy

RUN go build -o bot main.go

FROM alpine:latest

RUN apk add --no-cache zeromq

WORKDIR /app

COPY --from=builder /app/bot .

CMD ["./bot"]

