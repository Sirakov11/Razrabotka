from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flasgger import Swagger
import requests
import json
import os

app = Flask(__name__)
Swagger(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

USER_DATA_DIR = 'user_data'
os.makedirs(USER_DATA_DIR, exist_ok=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

USER_DATA_FILE = os.path.join(USER_DATA_DIR, 'users.json')
if not os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump([], f)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LiveList(Resource):
    """
    Live List endpoint.
    ---
    tags:
      - Football
    responses:
      200:
        description: A list of live items
    """
    @login_required
    def get(self):
        """
        Retrieve the live list.
        """
        return {'message': 'This is the live list'}

class LiveInPlaying(Resource):
    """
    Live In Playing endpoint.
    """
    def get(self):
        """
        Retrieve live in playing information.
        """
        url = "https://football-betting-odds1.p.rapidapi.com/provider1/live/inplaying"

        headers = {
            'X-RapidAPI-Key': "4a5c72287emsha6b89d62d93033bp17c46fjsncc8afd2f748d",
            'X-RapidAPI-Host': "football-betting-odds1.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers)
        return response.json()

class LiveMatch(Resource):
    """
    Live Match endpoint.
    """
    def get(self, match_id):
        """
        Retrieve information for a specific live match.
        ---
        parameters:
          - name: match_id
            in: path
            type: string
            required: true
            description: The ID of the live match
        responses:
          200:
            description: Information for the specified live match
        """
        url = f"https://football-betting-odds1.p.rapidapi.com/provider1/live/match/{match_id}"

        headers = {
            "X-RapidAPI-Key": "4a5c72287emsha6b89d62d93033bp17c46fjsncc8afd2f748d",
            "X-RapidAPI-Host": "football-betting-odds1.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers)
        return response.json()

class UpcomingMatches(Resource):
    """
    Upcoming Matches endpoint.
    """
    def get(self):
        """
        Retrieve information for upcoming matches.
        """
        url = "https://football-betting-odds1.p.rapidapi.com/provider1/live/upcoming"

        headers = {
            "X-RapidAPI-Key": "4a5c72287emsha6b89d62d93033bp17c46fjsncc8afd2f748d",
            "X-RapidAPI-Host": "football-betting-odds1.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers)
        
        try:
            all_upcoming_matches = response.json()
        except ValueError:
            all_upcoming_matches = []

        return all_upcoming_matches

class TopFiveLeagues(Resource):
    """
    Top Five Leagues endpoint.
    """
    @login_required
    def get(self):
        """
        Retrieve information for the top five football leagues.
        ---
        responses:
          200:
            description: Information for the top five football leagues
          500:
            description: Failed to parse response as JSON
        """
        url = "https://football-betting-odds1.p.rapidapi.com/provider1/live/upcoming"

        headers = {
            "X-RapidAPI-Key": "4a5c72287emsha6b89d62d93033bp17c46fjsncc8afd2f748d",
            "X-RapidAPI-Host": "football-betting-odds1.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers)

        try:
            all_upcoming_matches = response.json()
        except ValueError:
            return {'error': 'Failed to parse response as JSON'}, 500

        matches_info = []
        for matches_id, match_data in all_upcoming_matches.items():
            if isinstance(match_data, dict) and "country_leagues" in match_data:
                matches_info.append(match_data)

        filtered_matches = [match for match in matches_info if
                             match.get("country_leagues") in ["England - Premier League",
                                                               "Germany - Bundesliga",
                                                               "Italy - Serie A",
                                                               "France - Ligue 1",
                                                               "Spain - LaLiga"]]

        if not filtered_matches:
            return {'message': 'No matches found for the specified leagues.'}

        return filtered_matches

api = Api(app)
api.add_resource(LiveList, '/api/football/live/list')
api.add_resource(LiveInPlaying, '/api/football/live/inplaying')
api.add_resource(LiveMatch, '/api/football/live/match/<match_id>')
api.add_resource(UpcomingMatches, '/api/football/live/upcoming')
api.add_resource(TopFiveLeagues, '/api/football/live/upcoming/top5')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('topfiveleagues'))
        else:
            return 'Login failed. Invalid username or password.'
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_users = get_users()
        if username in existing_users:
            return 'Sign up failed. Username already exists.'

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

def get_users():
    with open(USER_DATA_FILE, 'r') as f:
        users = json.load(f)
    return users

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
