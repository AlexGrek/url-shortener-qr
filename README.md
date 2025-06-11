# 🔗 QR URL Shortener Service

A fast, lightweight URL shortening service built with **FastAPI**, featuring:

- 🚀 Shortened URL generation
- 📸 Base64-encoded QR code generation
- 🔒 API key-based access control
- 💾 Embedded persistent key-value storage
- 🧼 Automatic expiry + cleanup
- ☁️ Ready for Kubernetes via Helm

---

## 🌐 Public API

### `POST /api/create`

Create a new shortened URL with a QR code.

#### Request JSON

```json
{
  "ttl": 3600,                // Time-to-live in seconds
  "url": "https://example.com",
  "apikey": "your-secret-key",
  "reason": "custom analytics"
}
```

#### Response JSON

```json
{
  "short_url": "http://qr.example.com/aB34hC",
  "qr": "iVBORw0KGgoAAAANSUhEUgAA..."  // Base64-encoded PNG
}
```

### GET /{short_key}

Redirects to the original URL if it exists and hasn’t expired.
Returns a 404 HTML page if the key is invalid or expired.

## ⚙️ Makefile Commands

Use make to simplify development and deployment:

| Command                  | Description                                   |
| ------------------------ | --------------------------------------------- |
| `make run`               | Run the FastAPI app locally with Uvicorn      |
| `make helm_install`      | Install the service on Kubernetes using Helm  |
| `make helm_upgrade`      | Upgrade an existing Helm deployment           |
| `make docker-build-push` | Build and push Docker image to local registry |

## 📦 Deployment with Helm

This project comes with a customizable Helm chart:

```shell
helm upgrade --install url-shortener ./helm-chart \
  --set ingress.domain=yourdomain \
  --set apiKey=your-secret-key
```

## 🛠 Configurable via values.yaml:

```yaml
ingress:
  enabled: true
  domain: example       # Your base domain (used as qr.example.com)
  certResolver: le      # Let's Encrypt resolver

service:
  name: url-shortener
  port: 8000

persistence:
  enabled: true
  size: 1Gi

```

## 🐳 Docker Image

Build and push to your container registry:

```shell
docker build . -t localhost:5000/url-shortener:latest
docker push localhost:5000/url-shortener:latest
```

## 📂 Persistent Storage

The cache is backed by diskcache and persisted via a Kubernetes PersistentVolumeClaim. Default path: /app/url_cache.

## 🧼 Auto Cleanup

Expired entries are automatically removed from the cache:

- On application startup
- Every hour via background task

## 📜 License

MIT — do whatever you want, just don't abuse it.

