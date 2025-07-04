from flask import Flask, request, redirect, session, jsonify
import requests
import os
from dotenv import load_dotenv
from urllib.parse import urlencode
from pathlib import Path

# Load environment variables
load_dotenv(dotenv_path=Path('.') / '.env')

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

print("Client ID:", SPOTIFY_CLIENT_ID)
print("Redirect URI:", REDIRECT_URI)

app = Flask(__name__)
app.secret_key = os.urandom(24)

SCOPE = "user-top-read user-read-recently-played"
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"

@app.route('/')
def index():
    return '<a href="/login">Login with Spotify</a>'

@app.route('/login')
def login():
    params = {
        'client_id': SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE
    }
    login_url = f"{AUTH_URL}?{urlencode(params)}"
    print("Spotify login URL:", login_url)
    return redirect(login_url)

@app.route('/callback')
@app.route('/callback/')
def callback():
    code = request.args.get('code')
    error = request.args.get('error')
    print("Spotify returned code:", code)
    print("Spotify returned error:", error)

    if error:
        return f"Authorization failed: {error}", 400
    if not code:
        return 'Authorization failed: No code received', 400

    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET
    }

    auth_header = (SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    response = requests.post(TOKEN_URL, data=payload, auth=auth_header)
    token_info = response.json()
    print("Token info:", token_info)

    if 'access_token' not in token_info:
        return jsonify(token_info), 400

    session['access_token'] = token_info['access_token']
    return redirect('/top')

@app.route('/top')
def get_top_tracks():
    access_token = session.get('access_token')
    if not access_token:
        return redirect('/login')

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(
        'https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=10',
        headers=headers
    )

    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch top tracks'}), response.status_code

    return jsonify(response.json())

@app.route('/top-artists')
def get_top_artists():
    access_token = session.get('access_token')
    if not access_token:
        return redirect('/login')

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(
        'https://api.spotify.com/v1/me/top/artists?limit=50&time_range=long_term',
        headers=headers
    )

    if response.status_code != 200:
        print("Failed to fetch top artists")
        return jsonify({'error': 'Failed to fetch top artists'}), response.status_code

    data = response.json()

    print("\n🎵 Top 50 Artists:\n-------------------")
    for i, artist in enumerate(data['items'], start=1):
        print(f"{i}. {artist['name']}")

    return jsonify({'message': 'Top 50 artist names printed in console.'})


if __name__ == '__main__':
    app.run(debug=True)
