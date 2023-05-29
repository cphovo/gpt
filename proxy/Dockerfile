# 构建阶段 1：编译 Go 项目
FROM golang:1.20 AS builder

WORKDIR /app

COPY . .

RUN go mod download
RUN CGO_ENABLED=0 go build -ldflags="-w -s" -o myapp

# 构建阶段 2：生成最终镜像
FROM alpine:latest

EXPOSE 9090

WORKDIR /app

# 从构建阶段 1 中复制编译好的二进制文件
COPY --from=builder /app/myapp .

# 可选：复制其他运行时所需的文件或目录

# 设置入口点
CMD ["./myapp"]

