"""
EVE Online ESI - OAuth2 with PKCE using a localhost callback server.

Flow:
  1. Generate PKCE code_verifier + code_challenge
  2. Spin up a temporary HTTP server on a random port
  3. Open the browser to the EVE SSO authorization URL
  4. EVE redirects to http://127.0.0.1:{port}/callback?code=...
  5. Server captures the code, exchanges it for tokens, shuts down
  6. Tokens are returned to your application

Usage:
    python eve_oauth.py
"""

import base64
import hashlib
import http.server
import json
import os
import secrets
import socket
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Configuration — fill in your EVE developer app values
# ---------------------------------------------------------------------------
CLIENT_ID = "94cf39a145d8422eb72f9b7060f55c1a" # TODO: Client ID should be defined in caller's code


# Scopes you want to request (space-separated)
SCOPES = ["publicData","esi-calendar.respond_calendar_events.v1","esi-calendar.read_calendar_events.v1","esi-location.read_location.v1","esi-location.read_ship_type.v1","esi-mail.organize_mail.v1","esi-mail.read_mail.v1","esi-mail.send_mail.v1","esi-skills.read_skills.v1","esi-skills.read_skillqueue.v1","esi-wallet.read_character_wallet.v1","esi-wallet.read_corporation_wallet.v1","esi-search.search_structures.v1","esi-clones.read_clones.v1","esi-characters.read_contacts.v1","esi-universe.read_structures.v1","esi-killmails.read_killmails.v1","esi-corporations.read_corporation_membership.v1","esi-assets.read_assets.v1","esi-planets.manage_planets.v1","esi-fleets.read_fleet.v1","esi-fleets.write_fleet.v1","esi-ui.open_window.v1","esi-ui.write_waypoint.v1","esi-characters.write_contacts.v1","esi-fittings.read_fittings.v1","esi-fittings.write_fittings.v1","esi-markets.structure_markets.v1","esi-corporations.read_structures.v1","esi-characters.read_loyalty.v1","esi-characters.read_chat_channels.v1","esi-characters.read_medals.v1","esi-characters.read_standings.v1","esi-characters.read_agents_research.v1","esi-industry.read_character_jobs.v1","esi-markets.read_character_orders.v1","esi-characters.read_blueprints.v1","esi-characters.read_corporation_roles.v1","esi-location.read_online.v1","esi-contracts.read_character_contracts.v1","esi-clones.read_implants.v1","esi-characters.read_fatigue.v1","esi-killmails.read_corporation_killmails.v1","esi-corporations.track_members.v1","esi-wallet.read_corporation_wallets.v1","esi-characters.read_notifications.v1","esi-corporations.read_divisions.v1","esi-corporations.read_contacts.v1","esi-assets.read_corporation_assets.v1","esi-corporations.read_titles.v1","esi-corporations.read_blueprints.v1","esi-contracts.read_corporation_contracts.v1","esi-corporations.read_standings.v1","esi-corporations.read_starbases.v1","esi-industry.read_corporation_jobs.v1","esi-markets.read_corporation_orders.v1","esi-corporations.read_container_logs.v1","esi-industry.read_character_mining.v1","esi-industry.read_corporation_mining.v1","esi-planets.read_customs_offices.v1","esi-corporations.read_facilities.v1","esi-corporations.read_medals.v1","esi-characters.read_titles.v1","esi-alliances.read_contacts.v1","esi-characters.read_fw_stats.v1","esi-corporations.read_fw_stats.v1","esi-corporations.read_projects.v1","esi-corporations.read_freelance_jobs.v1","esi-characters.read_freelance_jobs.v1","esi-structures.read_corporation.v1","esi-structures.read_character.v1","esi-activities.read_character.v1","esi-access.read_lists.v1"]

# EVE SSO endpoints
EVE_AUTH_URL = "https://login.eveonline.com/v2/oauth/authorize"
EVE_TOKEN_URL = "https://login.eveonline.com/v2/oauth/token"

#CALLBACK_URL = "http://localhost:12534/callback"
CALLBACK_PORT = 12345

# How long to wait for the user to complete login (seconds)
#LOGIN_TIMEOUT = 300
LOGIN_TIMEOUT = 60


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class TokenResponse:
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str

    @property
    def as_json(self):
        return json.dumps({
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_in': self.expires_in,
            'token_type': self.token_type,
        })

    @classmethod
    def from_dict(cls, token_dict):
        return cls(
            access_token = token_dict['access_token'],
            refresh_token = token_dict['refresh_token'],
            expires_in = token_dict['expires_in'],
            token_type = token_dict['token_type'],
        )

    @classmethod
    def from_json(cls, token_json):
        token_dict = json.loads(token_json)
        return cls.from_dict(token_dict)


# ---------------------------------------------------------------------------
# PKCE helpers
# ---------------------------------------------------------------------------
def generate_pkce_pair() -> tuple[str, str]:
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32))  # keep as bytes
    sha256 = hashlib.sha256()
    sha256.update(code_verifier)
    code_challenge = base64.urlsafe_b64encode(sha256.digest()).decode().rstrip("=")
    return (code_verifier.decode(), code_challenge)  # decode only at the end

'''
def generate_pkce_pair() -> tuple[str, str]:
    """Return (code_verifier, code_challenge)."""
    # code_verifier: 32 random bytes → base64url, no padding
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode()

    # code_challenge: SHA-256 of verifier → base64url, no padding
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()

    return code_verifier, code_challenge
'''

# ---------------------------------------------------------------------------
# Localhost callback server
# ---------------------------------------------------------------------------
class _OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    """Handles a single GET /callback request from the browser."""

    # Injected by the server before it starts
    expected_state: str = ""
    result: dict = {}  # populated on success: {"code": ..., "error": ...}

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path != "/callback":
            self._respond(404, "Not found")
            return

        params = dict(urllib.parse.parse_qsl(parsed.query))

        # State validation — prevents CSRF
        if params.get("state") != self.server.expected_state:  # type: ignore[attr-defined]
            self._respond(400, "State mismatch — possible CSRF attack.")
            self.server.result["error"] = "state_mismatch"  # type: ignore[attr-defined]
        elif "error" in params:
            error_msg = params.get("error_description", params["error"])
            self._respond(400, f"Authorization error: {error_msg}")
            self.server.result["error"] = error_msg  # type: ignore[attr-defined]
        else:
            self._respond(
                200,
                "<h2>✅ Authorization successful!</h2>"
                "<p>You can close this tab and return to the application.</p>",
            )
            self.server.result["code"] = params["code"]  # type: ignore[attr-defined]

        # Signal the waiting thread that we're done
        self.server.shutdown_event.set()  # type: ignore[attr-defined]

    def _respond(self, status: int, body: str):
        html = f"<html><body style='font-family:sans-serif;padding:2em'>{body}</body></html>"
        encoded = html.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format, *args):
        # Suppress default stderr logging
        pass


class _CallbackServer(http.server.HTTPServer):
    """HTTPServer with extra attributes used by the handler."""

    def __init__(self, *args, expected_state: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.expected_state: str = expected_state
        self.result: dict = {}
        self.shutdown_event = threading.Event()


def _find_free_port() -> int:
    """Ask the OS for an available port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# ---------------------------------------------------------------------------
# Token exchange
# ---------------------------------------------------------------------------
'''
def _exchange_code_for_tokens(
    code: str,
    code_verifier: str,
    redirect_uri: str,
) -> TokenResponse:
    """POST the authorization code + PKCE verifier to get tokens."""
    payload = urllib.parse.urlencode(
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": CLIENT_ID,
            "code_verifier": code_verifier,
        }
    ).encode()

    req = urllib.request.Request(
        EVE_TOKEN_URL,
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "login.eveonline.com",
        },
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())

    return TokenResponse(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires_in=data["expires_in"],
        token_type=data["token_type"],
    )
'''

def _exchange_code_for_tokens(code, code_verifier, redirect_uri):
    import base64

    # Basic auth header: base64(client_id:client_secret)
    # For PKCE (no secret), EVE still needs the client_id in the body
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "login.eveonline.com",
    }
    payload = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": CLIENT_ID,       # required for PKCE (no secret flow)
        "code_verifier": code_verifier,
    }).encode()

    req = urllib.request.Request(
        EVE_TOKEN_URL,
        data=payload,
        headers=headers,
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())

    return TokenResponse(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires_in=data["expires_in"],
        token_type=data["token_type"],
    )

def refresh_access_token(refresh_token: str) -> TokenResponse:
    """Use a refresh token to obtain a new access token (call when expired)."""
    payload = urllib.parse.urlencode(
        {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID,
        }
    ).encode()

    req = urllib.request.Request(
        EVE_TOKEN_URL,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())

    return TokenResponse(
        access_token=data["access_token"],
        refresh_token=data.get("refresh_token", refresh_token),  # EVE may reuse old one
        expires_in=data["expires_in"],
        token_type=data["token_type"],
    )


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------
def authenticate(client_id) -> Optional[TokenResponse]:
    """
    Run the full OAuth2 + PKCE login flow.
    Opens the browser, waits for the callback, and returns tokens.
    Returns None if the user cancels or the timeout is reached.
    """
    code_verifier, code_challenge = generate_pkce_pair()
    state = secrets.token_urlsafe(16)  # CSRF protection
    port = CALLBACK_PORT

    redirect_uri = f"http://localhost:{port}/callback"

    #print(f"Redirect URI: {redirect_uri}") # <<<<<

    # Build the authorization URL
    auth_params = urllib.parse.urlencode(
        {
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "scope": ' '.join(SCOPES),
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        },
        quote_via = urllib.parse.quote
    )
    auth_url = f"{EVE_AUTH_URL}?{auth_params}"
    print(f"Auth URL: {auth_url}")


    # Start the callback server in a background thread
    server = _CallbackServer(
        ("127.0.0.1", port),
        _OAuthCallbackHandler,
        expected_state=state,
    )

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    print(f"Opening browser for EVE Online login...")
    print(f"If the browser doesn't open, visit:\n  {auth_url}\n")
    webbrowser.open(auth_url)

    # Wait for the callback (or timeout)
    received = server.shutdown_event.wait(timeout=LOGIN_TIMEOUT)
    server.shutdown()
    server_thread.join(timeout=5)

    if not received:
        print("Login timed out — no callback received within "
              f"{LOGIN_TIMEOUT} seconds.")
        return None

    if "error" in server.result:
        print(f"Login failed: {server.result['error']}")
        return None

    code = server.result["code"]
    print("Authorization code received. Exchanging for tokens...")

    tokens = _exchange_code_for_tokens(code, code_verifier, redirect_uri)
    print("Login successful!")
    return tokens


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    tokens = authenticate()

    if tokens:
        print(f"\nAccess token  : {tokens.access_token[:40]}...")
        print(f"Refresh token : {tokens.refresh_token[:40]}...")
        print(f"Expires in    : {tokens.expires_in}s")

        # --- Example: call the ESI API with the token ---
        # character_id = "12345678"
        # req = urllib.request.Request(
        #     f"https://esi.evetech.net/latest/characters/{character_id}/skills/",
        #     headers={"Authorization": f"Bearer {tokens.access_token}"},
        # )
        # with urllib.request.urlopen(req) as resp:
        #     skills = json.loads(resp.read())
        #     print(skills)