import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import os
import json
from datetime import datetime
import csv

import urllib.parse

# Configuration
client_id = os.environ.get('STRAVA_CLIENT_ID')
client_secret = os.environ.get('STRAVA_CLIENT_SECRET')
redirect_uri = 'http://localhost:8080/callback'
auth_url = 'http://www.strava.com/oauth/authorize'
token_url = 'https://www.strava.com/oauth/token'
scope = 'activity:read_all'

# Step 1: Redirect user to OAuth provider's authorization page
params = {
    'client_id': client_id,
    'response_type': 'code',
    'redirect_uri': redirect_uri,
    'scope': scope
}
auth_request_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
webbrowser.open(auth_request_url)

# Step 2: Handle the redirect back from the OAuth provider
class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if 'code' in query_components:
            auth_code = query_components['code'][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Authorization successful. You can close this window.')
            self.server.auth_code = auth_code
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Authorization failed.')

def get_auth_code():
    server = HTTPServer(('localhost', 8080), OAuthHandler)
    server.handle_request()
    return server.auth_code

auth_code = get_auth_code()

# Step 3: Exchange authorization code for access token
data = {
    'client_id': client_id,
    'client_secret': client_secret,
    'grant_type': 'authorization_code',
    'code': auth_code,
    'redirect_uri': redirect_uri
}
response = requests.post(token_url, data=data)
tokens = response.json()

access_token = tokens['access_token']
first_name = tokens['athlete']['firstname']
last_name = tokens['athlete']['lastname']

print(f"Hello {first_name} {last_name}!")

activities_file = 'activities.json'

if not os.path.exists(activities_file):
    activities = []
    headers = {'Authorization': f'Bearer {access_token}'}
    before = int(datetime(2025, 1, 1).timestamp())
    after = int(datetime(2024, 1, 1).timestamp())
    page = 1

    while True:
        params = {
            'before': before,
            'after': after,
            'per_page': 50,
            'page': page
        }
        print(params)
        response = requests.get('https://www.strava.com/api/v3/activities', headers=headers, params=params)
        data = response.json()
        print(f"Number of activities in page {page}: {len(data)}")
        if not data or page == 10:
            break
        activities.extend(data)
        page += 1

    with open(activities_file, 'w') as f:
        json.dump(activities, f)

if os.path.exists(activities_file):
    with open(activities_file, 'r', encoding='utf-8') as f:
        activities = json.load(f)

    csv_file = 'activities.csv'
    csv_columns = ['id', 'start_date', 'elapsed_time_seconds', 'distance_meters', 'type', 'name', 'total_elevation_gain_meters']

    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns, delimiter=';')
        writer.writeheader()
        for activity in activities:
            writer.writerow({
                 'id': activity.get('id'),
                 'start_date': activity.get('start_date'),
                 'elapsed_time_seconds': activity.get('elapsed_time'),
                 'distance_meters': str(activity.get('distance')).split('.')[0],
                 'type': activity.get('type'),
                 'name': activity.get('name'),
                 'total_elevation_gain_meters': str(activity.get('total_elevation_gain')).split('.')[0]
            })



