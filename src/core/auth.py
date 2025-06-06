import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from google.auth.transport.requests import Request

from . import config

# The scopes required for the YouTube Data API
SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube.readonly']

def get_credentials():
    """
    Handles Google API authentication flow.
    If credentials exist and are valid, returns them.
    Otherwise, initiates the OAuth2 flow to get new credentials.
    """
    creds = None
    # The file credentials.json stores the user's access and refresh tokens.
    if os.path.exists(config.CREDENTIALS_FILE):
        creds = google.oauth2.credentials.Credentials.from_authorized_user_file(config.CREDENTIALS_FILE, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Failed to refresh token: {e}")
                run_auth_flow()
        else:
            run_auth_flow()

        # Reload credentials after flow
        if os.path.exists(config.CREDENTIALS_FILE):
             creds = google.oauth2.credentials.Credentials.from_authorized_user_file(config.CREDENTIALS_FILE, SCOPES)
    
    return creds

def run_auth_flow():
    """Runs the authentication flow to get new credentials."""
    print("Running authentication flow...")
    if not os.path.exists(config.CLIENT_SECRETS_FILE):
        print(f"Error: Client secrets file not found at '{config.CLIENT_SECRETS_FILE}'")
        print("Please download it from the Google Cloud Console and place it in the 'data' directory.")
        return

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        config.CLIENT_SECRETS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    
    # Save the credentials for the next run
    with open(config.CREDENTIALS_FILE, 'w') as token:
        token.write(creds.to_json())
    print(f"Credentials saved to {config.CREDENTIALS_FILE}")


if __name__ == '__main__':
    print("Attempting to authenticate with Google API...")
    credentials = get_credentials()
    if credentials:
        print("Authentication successful.")
    else:
        print("Authentication failed. Please check the console for errors.")
