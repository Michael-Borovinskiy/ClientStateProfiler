FROM golang:1.23.6-alpine AS builder

RUN apk add --no-cache git

RUN git clone https://github.com/pixperk/chug.git /app
WORKDIR /app

RUN go build -o chug .

FROM alpine:latest

WORKDIR /root/

COPY --from=builder /app/chug .

COPY .chug.yaml .

ENTRYPOINT ["./chug"]
