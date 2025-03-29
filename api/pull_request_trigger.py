import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")
BASE_BRANCH = os.getenv("BASE_BRANCH")
HEAD_BRANCH = os.getenv("HEAD_BRANCH")
if not HEAD_BRANCH:
    raise ValueError("HEAD_BRANCH environment variable is not set")
TITLE = 'test'
BODY = 'test'

url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls"
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}
data = {
    "title": TITLE,
    "head": HEAD_BRANCH,
    "base": BASE_BRANCH,
    "body": BODY,
    "draft": True,
    "reviewers": ["thejaptime"],
    "assignees": ["tachingers"]
}

print(f"Creating PR from branch: {HEAD_BRANCH}")
response = requests.post(url, headers=headers, json=data)

if response.status_code == 201:
    pr_url = response.json()["html_url"]
    print(f"✅ Draft PR created: {pr_url}")
else:
    print(f"❌ Failed to create PR: {response.status_code}")
    print(response.text)