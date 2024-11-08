# Import Statements
# ----------------------------------------------------------------
import os

# ---

# ---
import flask
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
# ----------------------------------------------------------------

# File Docstring
# --------------------------------
# @author @MaxineToTheStars <https://github.com/MaxineToTheStars>
# ----------------------------------------------------------------

# Constants
__version__: str = "v0.1.0"

# Public Variables

# Private Variables
_app = flask.Flask(__name__, template_folder="templates")

# main

# Public Methods
@_app.post("/search")
def search():
    # Load credentials from the session
    credentials = Credentials(**flask.session["credentials"])

    # Create a Sheets API service
    sheets_service = build("sheets", "v4", credentials=credentials)

@_app.route("/home")
def home():
    # Show page
    return flask.render_template("home.html")

@_app.route("/")
def index():
    # Setup a control flow
    control_flow: Flow = Flow.from_client_secrets_file(
        "api.json", scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    # Configure the redirect URI
    control_flow.redirect_uri = "http://127.0.0.1:5000/callback"

    # Generate the OAuth URL and state
    auth_url, auth_state = control_flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )

    # Store in the session
    flask.session["state"] = auth_state

    # Prompt redirect
    return flask.redirect(auth_url)

# Private Methods
@_app.route("/callback")
def callback() -> None:
    # Retrieve state
    auth_state = flask.session["state"]

    # Create a new flow
    control_flow: Flow = Flow.from_client_secrets_file(
        "api.json",
        state=auth_state,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    control_flow.redirect_uri = flask.url_for("callback", _external=True)

    # Get the response
    auth_response = flask.request.url
    control_flow.fetch_token(authorization_response=auth_response)

    # Store the credentials
    credentials = control_flow.credentials
    flask.session["credentials"] = _credentials_to_dict(credentials)

    # Redirect
    return flask.redirect(flask.url_for("home"))

def _credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

# Script Check
if __name__ == "__main__":
    # Log
    print(f"Oh, the Data You'll See || Version: {__version__}")

    # Terrible but whatever
    _app.secret_key = "OhThePlacesWe'llGo"
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # Run with Flask
    _app.run(debug=True)
