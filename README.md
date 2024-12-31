# Pre-requisities

- Python
- Strava API credentials - [READ HERE](https://developers.strava.com/docs/getting-started/)

# Setup

From the git directory, execute:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

# Run

```powershell
$ENV:STRAVA_CLIENT_ID = "<your strava client_id>"
$ENV:STRAVA_CLIENT_SECRET = "<your strava client_secret>"

python export.py
```