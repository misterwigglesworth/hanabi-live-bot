#!/usr/bin/env python

# An example reference bot for the Hanab Live website
# Written by Zamiel

import sys
from util import printf

# The "dotenv" module does not work in Python 2
if sys.version_info < (3, 0):
    printf("This script requires Python 3.x.")
    sys.exit(1)

# Imports (standard library)
import os

# Imports (3rd-party)
import dotenv
import requests

# Imports (local application)
from hanabi_client import HanabiClient


# Authenticate, login to the WebSocket server, and run forever
def main():
    # Check to see if the ".env" file exists
    env_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), ".env")
    if not os.path.exists(env_path):
        printf(
            'error: the ".env" file does not exist; copy the ".env_template" file to ".env" and edit the values accordingly'
        )
        sys.exit(1)

    # Load environment variables from the ".env" file
    dotenv.load_dotenv()

    use_localhost = os.getenv("USE_LOCALHOST")
    if use_localhost == "":
        printf('error: "USE_LOCALHOST" is blank in the ".env" file')
        sys.exit(1)
    if use_localhost == "true":
        use_localhost = True
    elif use_localhost == "false":
        use_localhost = False
    else:
        printf(
            'error: "USE_LOCALHOST" should be set to either "true" or "false" in the ".env" file'
        )
        sys.exit(1)

    username = os.getenv("HANABI_USERNAME")
    if username == "":
        printf('error: "HANABI_USERNAME" is blank in the ".env" file')
        sys.exit(1)

    password = os.getenv("HANABI_PASSWORD")
    if password == "":
        printf('error: "HANABI_PASSWORD" is blank in the ".env" file')
        sys.exit(1)

    # Get an authenticated cookie by POSTing to the login handler
    if use_localhost:
        # Assume that we are not using a certificate if we are running a local
        # version of the server
        protocol = "http"
        ws_protocol = "ws"
        host = "localhost"
    else:
        # The official site uses HTTPS
        protocol = "https"
        ws_protocol = "wss"
        host = "hanab.live"
    path = "/login"
    ws_path = "/ws"
    url = protocol + "://" + host + path
    ws_url = ws_protocol + "://" + host + ws_path
    printf('Authenticating to "' + url + '" with a username of "' + username + '".')
    resp = requests.post(
        url,
        {
            "username": username,
            "password": password,
            # This is normally the version of the JavaScript client,
            # but it will also accept "bot" as a valid version
            "version": "bot",
        },
    )

    # Handle failed authentication and other errors
    if resp.status_code != 200:
        printf("Authentication failed:")
        printf(resp.text)
        sys.exit(1)

    # Scrape the cookie from the response
    cookie = ""
    for header in resp.headers.items():
        if header[0] == "Set-Cookie":
            cookie = header[1]
            break
    if cookie == "":
        printf("Failed to parse the cookie from the authentication response headers:")
        printf(resp.headers)
        sys.exit(1)

    HanabiClient(ws_url, cookie)


if __name__ == "__main__":
    main()
