from flask import Flask, request, redirect, session, jsonify
import requests
import os
from dotenv import load_dotenv
from urllib.parse import urlencode
from pathlib import Path
from flask_cors import CORS
from flask_session import Session

app = Flask(__name__)

app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.secret_key = "tempsecretkey"
app.config.update(
      SESSION_COOKIE_DOMAIN="127.0.0.1",
      SESSION_COOKIE_SAMESITE="Lax",
      SESSION_COOKIE_SECURE=False
  )
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"]
)
# Load environment variables
load_dotenv(dotenv_path=Path('.') / '.env')

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

print("Client ID:", SPOTIFY_CLIENT_ID)
print("Redirect URI:", REDIRECT_URI)


SCOPE = "user-top-read user-read-recently-played"
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"



@app.route('/test-cors')
def test_cors():
    return 'CORS is working!'

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

    payload = {
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': REDIRECT_URI,
    }
    response = requests.post(TOKEN_URL, data=payload, auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET))

    token_info = response.json()
    print("Token info:", token_info)

    if 'access_token' not in token_info:
        return jsonify(token_info), 400

    session['access_token'] = token_info['access_token']
    print("Stored in session:", session.get('access_token'))
    return redirect('http://127.0.0.1:5173/wrapped')

@app.route('/wrapped')
def wrapped():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({'error': 'Not authenticated'}), 401

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(
        'https://api.spotify.com/v1/me/top/artists?limit=4&time_range=long_term',
        headers=headers
    )

    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch top artists'}), response.status_code

    #gets and returns top 4 artists and puts it on the page
    data = response.json()
    artists = data.get('items', [])
    top_artists = [{'name': artist['name']} for artist in artists[:4]]

    return jsonify({'top_artists': top_artists})

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
        return jsonify({
            'error': 'Failed to fetch top artists',
            'details': response.json()
        }), response.status_code

    data = response.json()
    artists = data.get('items', [])

    print("\n🎵 Your Top 50 Spotify Artists (long_term):")
    print("------------------------------------------")
    for i, artist in enumerate(artists, start=1):
        print(f"{i}. {artist['name']}")

    return jsonify({'message': 'Top 50 artists printed to console.'})

@app.route('/api/top-artists')
def get_top_artists_api():
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
        return jsonify({
            'error': 'Failed to fetch top artists',
            'details': response.json()
        }), response.status_code

    data = response.json()
    artists = data.get('items', [])

    print("\n🎵 Your Top 50 Spotify Artists (long_term):")
    print("------------------------------------------")
    for i, artist in enumerate(artists, start=1):
        print(f"{i}. {artist['name']}")

    return jsonify({'message': 'Top 50 artists printed to console.'})

if __name__ == '__main__':
    app.run(debug=True, port=5001)