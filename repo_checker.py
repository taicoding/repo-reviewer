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
    owner = parts[0]
    repo = parts[1]
    url = f"https://api.github.com/repos/{owner}/{repo}"
    return owner, repo, url

def check_file_exists(url, path):
    url = f"{url}/contents/{path}"
    response = requests.get(url, headers=HEADERS)
    return response.status_code == 200

def check_commit_dates(url, path, max_date):
    max_date = datetime.fromisoformat(max_date)
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

def check_issue_exists(url, issue_title, state="open"):
    url = f"{url}/issues"
    params = {"state": state, "per_page": 100}
    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return False

    issues = response.json()

    for issue in issues:
        if issue["title"].strip() == issue_title.strip():
            return True

    return False

def create_issue(url,owner, repo, body, title):
    url = f"{url}/issues"
    payload = {"title": title, "body": body}
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 201:
        print(f"Issue {title} created on {owner}/{repo}")
    else:
        print(f"Error at issue {title} creation on {owner}/{repo}: {response.status_code} - {response.text}")





