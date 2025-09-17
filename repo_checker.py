import os
import logging
from urllib.parse import urlparse
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from github import Github, Auth, GithubException

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
auth = Auth.Token(GITHUB_TOKEN)
gh = Github(auth=auth)

logging.basicConfig(level=logging.INFO)


def get_repo(owner, repo_name):
    try:
        return gh.get_user(owner).get_repo(repo_name)
    except GithubException as e:
        logging.error(f"Repo fetch error: {e}")
        return None


def format_url(repo_url):
    parts = urlparse(repo_url).path.strip("/").split("/")
    owner, repo_name = parts[:2]
    url = f"https://api.github.com/repos/{owner}/{repo_name}"
    return owner, repo_name, url


def check_fork(repo, parent_repo):
    return repo.fork and repo.parent.full_name.lower() == parent_repo.lower()


def check_branch_exists(repo, branch):
    try:
        repo.get_branch(branch)
        return True
    except GithubException as e:
        logging.warning(f"Branch check error: {e}")
        return False


def check_activity(repo, branch="main"):
    try:
        commits = repo.get_commits(sha=branch)
        return commits.totalCount > 0
    except GithubException as e:
        logging.warning(f"Activity check error: {e}")
        return False


def get_code_from_file(repo, path, branch="main"):
    try:
        file_content = repo.get_contents(path, ref=branch)
        if file_content.size:
            return file_content.decoded_content.decode()
        logging.info(f"File {path} is empty.")
        return ""
    except GithubException as e:
        logging.warning(f"File fetch error: {e}")
        return ""


def check_file_exists(repo, path, branch="main"):
    try:
        repo.get_contents(path, ref=branch)
        return True
    except GithubException as e:
        logging.warning(f"File existence check error: {e}")
        return False


def check_commit_dates(repo, path, max_date, branch="main", tz_name="America/La_Paz"):
    try:
        tz = ZoneInfo(tz_name)
        max_date = datetime.fromisoformat(max_date).replace(tzinfo=tz)
        commits = repo.get_commits(path=path, sha=branch)
        if commits.totalCount:
            last_commit = commits[0]
            file_date = last_commit.commit.author.date.astimezone(tz)
            return file_date.date() <= max_date.date()
        logging.info(f"No commits found for {path}")
        return None

    except GithubException as e:
        logging.warning(f"Commit date check error: {e}")
        return None


def check_issue_exists(repo, issue_title, state="open"):
    try:
        issues = repo.get_issues(state=state)
        return any(issue.title.strip() == issue_title.strip() for issue in issues)
    except GithubException as e:
        logging.warning(f"Issue check error: {e}")
        return False


def create_issue(repo, title, body):
    try:
        issue = repo.create_issue(title=title, body=body)
        return issue.html_url
    except GithubException as e:
        logging.error(f"Issue creation error: {e}")
        return None


def create_pr_fork(repo, title, body, head_branch, base_branch="main"):
    try:

        pr = repo.create_pull(
            title=title, body=body, head=head_branch, base=base_branch
        )
        return pr.html_url
    except GithubException as e:
        logging.error(f"PR creation error: {e}")
        return None
