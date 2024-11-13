#Spotify Flask Project

A simple Flask project that allows you to retrieve and display information from your Spotify account, such as your most listened-to artists and tracks. This project uses the Spotify API to interact with your account and display information about the artists and songs you like.

Features

- Login with Spotify API via OAuth.
- Display your most listened-to artists and tracks from your Spotify account.
- Search for artists and tracks with detailed information.
- Homepage with a menu to navigate between different features.

Prerequisites

Before you get started, make sure you have the following installed:

- Python 3.x
- Pip (Python package manager)
- A Spotify account and API credentials (Client ID, Client Secret).

Installation

1. Clone this repository to your local machine:
   git clone https://github.com/lahlousaad4/Spotify-insights.git
   cd Spotify-insights

2. Create a virtual environment (optional but recommended):
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate

3. Install the required dependencies:
   pip install -r requirements.txt

4. Go to [Spotify for Developers](https://developer.spotify.com), create an application (in redirects links, put http://127.0.0.1:5000/callback). After that, copy the Client ID and Client Secret.

5. Generate a secret key for your flask application, you can use os.urandom(24).

6. Create a .env file at the root of the project based on the .env.exemple file:
   CLIENT_ID=your_spotify_client_id
   CLIENT_SECRET=your_spotify_client_secret
   REDIRECT_URI=http://127.0.0.1:5000/callback
   FLASK_SECRET_KEY=your_flask_secret_key

7. Run the Flask application:
   python src/app.py

8. You can now access the application at http://127.0.0.1:5000.

Project Structure

- src/ : Contains the project files.
- app.py : The main Flask application file.
- templates/ : Contains the HTML templates for the user interface.
- requirements.txt : A list of the project's dependencies (Flask, Spotipy, etc.).
- .env.exemple : An example configuration file for environment variables.

Example .env (.env.example)

The .env.exemple file contains the necessary environment variables for the application to function. Example:

CLIENT_ID=your_spotify_client_id
CLIENT_SECRET=your_spotify_client_secret
REDIRECT_URI=http://127.0.0.1:5000/callback
FLASK_SECRET_KEY=your_flask_secret_key

Contribution

Contributions are welcome! If you have suggestions for improvements or bug fixes, feel free to open an issue or submit a pull request.
