import os
import requests
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def format_url(repo_url):
    parts = urlparse(repo_url).path.strip("/").split("/")
    return f"https://api.github.com/repos/{parts[0]}/{parts[1]}"

def check_file_exists(url, path):
    url = f"{url}/contents/{path}"
    response = requests.get(url, headers=HEADERS)
    return response.status_code == 200

def check_commit_dates(url, path, max_date):
    url = f"{url}/commits"
    params = {"path": path, "per_page": 100}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None

    commits = response.json()

    last_commit = commits[-1]
    file_date = datetime.fromisoformat(last_commit["commit"]["committer"]["date"])
    
    return file_date.date() <= max_date.date()





