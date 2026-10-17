import json
from js import Response, Headers

API_KEY = "ak_gf6ststb3ob15ey0auzxh7ru"
USER_EMAIL = "23f2002620@ds.study.iitm.ac.in"

async def on_fetch(request, env):
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, X-API-Key",
        "Content-Type": "application/json"
    }

    # Handle CORS preflight request
    if request.method == "OPTIONS":
        return Response.new(None, status=204, headers=Headers.new(cors_headers))

    # Authenticate X-API-Key header
    api_key_header = request.headers.get("X-API-Key")
    if not api_key_header or api_key_header != API_KEY:
        return Response.new(
            json.dumps({"error": "Unauthorized"}),
            status=401,
            headers=Headers.new(cors_headers)
        )

    if request.method != "POST":
        return Response.new(
            json.dumps({"error": "Method Not Allowed"}),
            status=405,
            headers=Headers.new(cors_headers)
        )

    try:
        req_text = await request.text()
        body = json.loads(req_text) if req_text else {}
        events = body.get("events", [])

        total_events = len(events)
        unique_users = len(set(e.get("user") for e in events if "user" in e))

        revenue = 0.0
        user_positive_totals = {}

        for event in events:
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
            headers=Headers.new(cors_headers)
        )
    except Exception as e:
        return Response.new(
            json.dumps({"error": "Invalid JSON or request structure"}),
            status=400,
            headers=Headers.new(cors_headers)
        )