# Dockerfile for Slay Check

# Build stage
FROM golang:1.21-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git make

# Set working directory
WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN make build-all

# Runtime stage
FROM alpine:latest

# Install runtime dependencies
RUN apk --no-cache add ca-certificates tzdata

# Create non-root user
RUN adduser -D -s /bin/sh slaycheck

# Set working directory
WORKDIR /app

# Copy binaries from builder stage
COPY --from=builder /app/bin/slay-check-linux-amd64 /usr/local/bin/slay-check

# Make binary executable
RUN chmod +x /usr/local/bin/slay-check

# Switch to non-root user
USER slaycheck

# Expose port (if needed for future web interface)
EXPOSE 8080

# Default command
ENTRYPOINT ["slay-check"]
CMD ["--help"]
