import json
from js import Response, Headers

API_KEY = "ak_gf6ststb3ob15ey0auzxh7ru"
USER_EMAIL = "23f2002620@ds.study.iitm.ac.in"

def get_cors_headers():
    """Builds a valid JS Headers object for Pyodide interop."""
    h = Headers.new()
    h.append("Access-Control-Allow-Origin", "*")
    h.append("Access-Control-Allow-Methods", "POST, OPTIONS")
    h.append("Access-Control-Allow-Headers", "Content-Type, X-API-Key, x-api-key")
    h.append("Content-Type", "application/json")
    return h

async def on_fetch(request, env):
    cors_headers = get_cors_headers()

    # Handle CORS preflight OPTIONS request
    if request.method == "OPTIONS":
        return Response.new("", status=204, headers=cors_headers)

    # Extract API Key header (case-insensitive check)
    api_key = request.headers.get("X-API-Key") or request.headers.get("x-api-key")
    if not api_key or api_key != API_KEY:
        return Response.new(
            json.dumps({"error": "Unauthorized"}),
            status=401,
            headers=cors_headers
        )

    if request.method != "POST":
        return Response.new(
            json.dumps({"error": "Method Not Allowed"}),
            status=405,
            headers=cors_headers
        )

    try:
        req_text = await request.text()
        body = json.loads(req_text) if req_text else {}
        events = body.get("events", [])

        total_events = len(events)
        unique_users = len(set(e.get("user") for e in events if isinstance(e, dict) and "user" in e))

        revenue = 0.0
        user_positive_totals = {}

        for event in events:
            if not isinstance(event, dict):
                continue
            user = event.get("user", "")
            try:
                amount = float(event.get("amount", 0))
            except (ValueError, TypeError):
                amount = 0.0

            if amount > 0:
                revenue += amount
                user_positive_totals[user] = user_positive_totals.get(user, 0.0) + amount

        top_user = ""
        max_revenue = -1.0
        for user, total in user_positive_totals.items():
            if total > max_revenue:
                max_revenue = total
                top_user = user

        payload = {
            "email": USER_EMAIL,
            "total_events": total_events,
            "unique_users": unique_users,
            "revenue": revenue,
            "top_user": top_user
        }

        return Response.new(
            json.dumps(payload),
            status=200,
            headers=cors_headers
        )
    except Exception as e:
        return Response.new(
            json.dumps({"error": "Invalid JSON"}),
            status=400,
            headers=cors_headers
        )