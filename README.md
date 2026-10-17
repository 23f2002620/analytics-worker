# Analytics Worker (Cloudflare Workers + Python)

A stateless event aggregation API built with Cloudflare Workers and Python using Pyodide. The endpoint authenticates incoming event batches through an `X-API-Key` header and calculates analytics in real time, with CORS support for browser-based clients.

## Deployed Endpoint

- **URL:** https://analytics-worker.saravanank171205.workers.dev/analytics
- **HTTP Method:** `POST`
- **Authentication:** `X-API-Key` header

> **Security note:** The API key included in examples should be treated as a secret. If it is a real, active key, rotate it and store the replacement as a Cloudflare Worker secret rather than committing it to a public repository.

---

## API Specification

### Request Headers

| Header | Value | Description |
|---|---|---|
| `Content-Type` | `application/json` | Indicates that the request body contains JSON. |
| `X-API-Key` | Your configured API key | Authenticates the request. Missing or invalid keys should return `401 Unauthorized`. |

### Example Request Body

```json
{
  "events": [
    {"user": "alice", "amount": 42.5, "ts": 1700000000},
    {"user": "bob", "amount": -10.0, "ts": 1700000001},
    {"user": "alice", "amount": 10.0, "ts": 1700000002},
    {"user": "charlie", "amount": 100.0, "ts": 1700000003}
  ]
}
```

Each event contains:

- `user`: User identifier.
- `amount`: Numeric amount associated with the event.
- `ts`: Event timestamp represented as a Unix timestamp.

### Example Response

**HTTP `200 OK`**

```json
{
  "email": "your_email@example.com",
  "total_events": 4,
  "unique_users": 3,
  "revenue": 152.5,
  "top_user": "charlie"
}
```

The email value above is a placeholder; the actual response should use the configured account owner's email address.

### Aggregation Rules

| Field | Description |
|---|---|
| `total_events` | Total number of events in the input array. |
| `unique_users` | Number of distinct user identifiers. |
| `revenue` | Sum of all positive `amount` values. Zero and negative amounts are excluded. |
| `top_user` | User with the highest cumulative positive revenue. |
| `email` | Configured account owner's email address. |

For the sample input, the positive amounts are `42.5`, `10.0`, and `100.0`, giving total revenue of `152.5`. Alice's cumulative positive revenue is `52.5`, while Charlie's is `100.0`, making Charlie the top user.

---

## Testing the Endpoint

### 1. Check CORS Preflight (`OPTIONS`)

Use this command to inspect the server's CORS preflight response:

```bash
curl -i -X OPTIONS \
  "https://analytics-worker.saravanank171205.workers.dev/analytics" \
  -H "Origin: https://example.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: X-API-Key, Content-Type"
```

Check that the response includes the appropriate CORS headers, including the allowed origin, method, and request headers.

### 2. Send an Event Batch (`POST`)

Set your API key in an environment variable before running the request:

```bash
export ANALYTICS_API_KEY="your_actual_api_key"
```

Then send the request:

```bash
curl -i -X POST \
  "https://analytics-worker.saravanank171205.workers.dev/analytics" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${ANALYTICS_API_KEY}" \
  -d '{
    "events": [
      {"user": "alice", "amount": 42.5, "ts": 1700000000},
      {"user": "bob", "amount": -10.0, "ts": 1700000001},
      {"user": "alice", "amount": 10.0, "ts": 1700000002},
      {"user": "charlie", "amount": 100.0, "ts": 1700000003}
    ]
  }'
```

Replace `your_actual_api_key` with the configured key. Avoid putting real credentials in shell scripts that may be committed to Git.

### 3. Test Authentication

Send a request without the `X-API-Key` header or with an invalid key. The expected behavior is an HTTP `401 Unauthorized` response, provided the Worker implements the documented authentication rules.

---

## Repository Structure

```text
.
├── src/
│   └── entry.py       # Python Worker entrypoint
├── wrangler.toml      # Wrangler configuration
└── README.md          # Project documentation
```

The exact structure may vary depending on the Cloudflare Workers Python template used by the project.

---

## Deployment

Deploy updates to Cloudflare Workers using either of the following methods.

### Option 1: Git Integration

If the Cloudflare Worker is connected to your Git repository:

1. Commit your changes.
2. Push them to the configured deployment branch, such as `main`.
3. Check the Cloudflare dashboard to confirm that the deployment completed successfully.

### Option 2: Wrangler CLI

Install the project dependencies and configure Wrangler according to your repository's setup. Then run:

```bash
npx wrangler login
npx wrangler deploy
```

Ensure `wrangler.toml` is configured for the correct Worker and entrypoint before deploying.

---

## Security Considerations

- Store API keys as Cloudflare Worker secrets; do not hardcode them in source files.
- Rotate any credentials accidentally committed to a public repository.
- Validate the request body and ensure `amount` is numeric and `user` is valid before aggregation.
- Configure CORS to allow only the origins that need access.
- Return appropriate HTTP status codes for authentication failures and malformed requests.
