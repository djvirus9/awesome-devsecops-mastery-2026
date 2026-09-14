"""Small, read-only training API with explicit authentication and ownership."""

import hmac
import json
import os
from datetime import datetime, timezone

from flask import Flask, jsonify, request

ITEMS = (
    {"id": "item-1", "name": "Alice's training item", "owner": "alice"},
    {"id": "item-2", "name": "Bob's training item", "owner": "bob"},
)


def load_tokens(raw: str) -> dict[str, str]:
    """Invalid configuration fails without including secret values in errors."""
    try:
        tokens = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        raise ValueError("API_TOKENS_JSON must be a JSON object") from None
    if not isinstance(tokens, dict) or any(
        not isinstance(token, str)
        or not token.isascii()
        or not token
        or len(token) > 256
        or any(character.isspace() for character in token)
        or not isinstance(owner, str)
        or not owner
        for token, owner in tokens.items()
    ):
        raise ValueError("API_TOKENS_JSON must map nonempty ASCII tokens to owners")
    return tokens


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(MAX_CONTENT_LENGTH=16384)
    if config:
        app.config.update(config)
    tokens = load_tokens(app.config.get("API_TOKENS_JSON", os.getenv("API_TOKENS_JSON", "{}")))

    def actor() -> str | None:
        authorization = request.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return None
        supplied = authorization[7:]
        if not supplied or not supplied.isascii() or len(supplied) > 256:
            return None
        for token, owner in tokens.items():
            if hmac.compare_digest(supplied, token):
                return owner
        return None

    def denied(status: int, owner: str = "unknown"):
        app.logger.warning(json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "request_denied",
            "subject": owner,
            "status": status,
        }))
        response = jsonify({"error": "unauthorized" if status == 401 else "not_found"})
        response.status_code = status
        if status == 401:
            response.headers["WWW-Authenticate"] = "Bearer"
        return response

    @app.after_request
    def response_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        return response

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/v1/items")
    def items():
        owner = actor()
        if owner is None:
            return denied(401)
        return jsonify({"items": [
            {"id": item["id"], "name": item["name"]}
            for item in ITEMS if item["owner"] == owner
        ]})

    @app.get("/v1/items/<item_id>")
    def item_detail(item_id: str):
        owner = actor()
        if owner is None:
            return denied(401)
        for item in ITEMS:
            if item["id"] == item_id and item["owner"] == owner:
                return jsonify({"id": item["id"], "name": item["name"]})
        return denied(404, owner)

    @app.errorhandler(404)
    def missing_route(_error):
        return jsonify({"error": "not_found"}), 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=False)
