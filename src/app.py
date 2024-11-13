import requests
import base64
from flask import Flask, redirect, request, session, url_for, render_template
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from dotenv import load_dotenv


load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope = "user-top-read user-follow-read" ))

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

# Étape 1 : Redirection pour autorisation
@app.route('/')
def login():
    scope = "user-top-read"
    auth_url = (
        "https://accounts.spotify.com/authorize"
        f"?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"
        f"&scope={scope}"
    )
    return redirect(auth_url)

# Étape 2 : Récupération du token d'accès
@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = "https://accounts.spotify.com/api/token"

    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    headers = {
        'Authorization': f"Basic {b64_auth_str}"
    }
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }

    response = requests.post(token_url, data=payload, headers=headers)
    response_data = response.json()

    if 'access_token' not in response_data:
        return f"Erreur: {response_data.get('error_description', 'Une erreur est survenue.')}"

    session['access_token'] = response_data['access_token']

    return redirect(url_for('index'))

# Étape 3 : Menu d'accueil
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('query')
    search_results = spotify_search(query)
    return render_template('search_results.html', results=search_results)



@app.route('/top-artists')
def top_artists():
    time_range = request.args.get('time_range', 'short_term')
    limit = request.args.get('limit', 50)
    response_data = fetch_top_artists(time_range, limit)
    top_artists_with_index = [(index + 1, artist) for index, artist in enumerate(response_data)]
    return render_template('top_artists.html', top_artists=top_artists_with_index, time_range=time_range)


@app.route('/top-songs')
def top_songs():
    time_range = request.args.get('time_range', 'short_term')
    limit = request.args.get('limit', 50)
    response_data = fetch_top_songs(time_range, limit)
    top_songs_with_index = [(index + 1, song) for index, song in enumerate(response_data)]
    return render_template('top_songs.html', top_songs=top_songs_with_index, time_range=time_range)


@app.route('/top-genres')
def top_genres():
    time_range = request.args.get('time_range', 'short_term')
    limit = request.args.get('limit', 50)
    response_data = fetch_top_genres(time_range, limit)

    top_genres_with_index = [(index + 1, genre, count, percentage)
                             for index, (genre, count, percentage) in enumerate(response_data)]

    return render_template('top_genres.html', top_genres=top_genres_with_index, time_range=time_range)



def fetch_top_artists(time_range, limit=50):
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    top_artists_url = f"https://api.spotify.com/v1/me/top/artists?time_range={time_range}&limit={limit}"
    artists_response = requests.get(top_artists_url, headers=headers)

    return [
        {
            'name': artist['name'],
            'image_url': artist['images'][0]['url'],
            'url': artist['external_urls']['spotify']
        }
        for artist in artists_response.json().get('items', [])
    ]

def fetch_top_songs(time_range, limit=50):
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    top_tracks_url = f"https://api.spotify.com/v1/me/top/tracks?time_range={time_range}&limit={limit}"
    tracks_response = requests.get(top_tracks_url, headers=headers)

    return [
        {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'image_url': track['album']['images'][0]['url'],
            'url': track['external_urls']['spotify']
        }
        for track in tracks_response.json().get('items', [])
    ]

def fetch_top_genres(time_range, limit):
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    top_artists_url = f"https://api.spotify.com/v1/me/top/artists?time_range={time_range}&limit={limit}"
    artists_response = requests.get(top_artists_url, headers=headers)
    artists = artists_response.json().get('items', [])

    genre_count = {}
    total_artists = len(artists)

    for artist in artists:
        genres = artist.get('genres', [])
        for genre in genres:
            if genre in genre_count:
                genre_count[genre] += 1
            else:
                genre_count[genre] = 1

    sorted_genres = sorted(genre_count.items(), key=lambda item: item[1], reverse=True)

    genre_percentage = [(genre, count, (count / total_artists) * 100) for genre, count in sorted_genres]

    return genre_percentage


def spotify_search(query):
    results = sp.search(q=query, type='artist', limit=10)
    print("Réponse de l'API:", results)

    artists = results.get('artists', {}).get('items', [])
    artist_results = []

    for artist in artists:
        artist_info = sp.artist(artist['id'])
        artist_url = artist['external_urls']['spotify']
        artist_info = {
            'id': artist['id'],
            'name': artist['name'],
            'image_url': artist['images'][0]['url'] if artist['images'] else None,
            'genres': artist.get('genres', []),
            'url': artist_url
        }

        artist_results.append(artist_info)

    track_results = []

    for artist in artist_results:
        top_tracks = sp.artist_top_tracks(artist['id'])

        for track in top_tracks['tracks'][:5]:
            track_info = {
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'streams': None,
                'album_name': track['album']['name'],
                'album_image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'release_date': track['album']['release_date'],
                'duration': track['duration_ms'] / 1000,
                'url': track['external_urls']['spotify']
            }

            track_results.append(track_info)

    return {'artists': artist_results, 'tracks': track_results}

@app.route('/artist/<artist_id>')
def artist_details(artist_id):
    artist = sp.artist(artist_id)
    top_tracks = sp.artist_top_tracks(artist_id)

    artist_url = artist['external_urls']['spotify']
    monthly_listeners, biographie, villes_details = get_monthly_listeners(artist_url)

    artist_details = {
        'name': artist['name'],
        'image_url': artist['images'][0]['url'] if artist['images'] else None,
        'genres': artist.get('genres', []),
        'biography': biographie,
        'monthly_listeners': monthly_listeners,
        'top_tracks': [{
                    'name': track['name'],
                    'url': track['external_urls']['spotify'],
                    'artist': track['artists'][0]['name'],
                    'album_name': track['album']['name']
                } for track in top_tracks['tracks'][:5]],
        'cities': villes_details
    }

    return render_template('artist_details.html', artist=artist_details)

#SELENIUM-SCRAPPING
def get_monthly_listeners(artist_url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    monthly_listeners = "Inconnu"
    biographie = "Biographie non disponible"
    villes_details = []

    try:
        driver.get(artist_url)
        time.sleep(5)
        try:
            accept_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Accepter')]")
            accept_button.click()
            time.sleep(4)
        except NoSuchElementException:
            pass
        time.sleep(3)
        listeners_element = driver.find_element(By.CSS_SELECTOR, '.Ydwa1P5GkCggtLlSvphs')
        monthly_listeners = listeners_element.text.strip().replace(' auditeurs mensuels', '')
        driver.find_element(By.CSS_SELECTOR, '.jW4eWdr_LUeOXwPpKhWG').click()
        time.sleep(3)
        biographie_element = driver.find_element(By.XPATH, '/html/body/div[20]/div/div/div/div[2]/div/div/div[2]/div[1]/p')
        biographie = biographie_element.text.strip()

        for i in range(3, 8):
            try:
                city_div = driver.find_element(By.XPATH, f'/html/body/div[20]/div/div/div/div[2]/div/div/div[1]/div[{i}]')
                city_name = city_div.find_element(By.XPATH, './div[1]').text.strip()
                city_info = city_div.find_element(By.XPATH, './div[2]').text.strip()
                villes_details.append((city_name, city_info))
            except Exception as e:
                print(f"Erreur lors de la récupération des détails de la ville {i}: {e}")

    except Exception as e:
        print(f"Erreur lors de la récupération des informations : {e}")

    finally:
        driver.quit()

    return monthly_listeners, biographie, villes_details




if __name__ == '__main__':
    app.run(debug=True)
