import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")
# BASE_BRANCH = os.getenv("BASE_BRANCH")
# HEAD_BRANCH = os.getenv("HEAD_BRANCH")

def create_pr(head_branch, base_branch):
    if not head_branch:
        raise ValueError("HEAD_BRANCH is needed")
    if not base_branch:
        raise ValueError("BASE_BRANCH is needed")

    TITLE = 'test'
    BODY = 'test'

    # Use the branch names directly without prefixing
    head = head_branch
    base = base_branch

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    data = {
        "title": TITLE,
        "head": head,
        "base": base,
        "body": BODY,
        "draft": True
    }

    print(f"Creating PR from branch '{head}' to '{base}'")
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        pr_url = response.json()["html_url"]
        pr_number = response.json()["number"]
        print(f"✅ Draft PR created: {pr_url}")

        # Add reviewers and assignees in a separate request
        review_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}/requested_reviewers"
        assign_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{pr_number}/assignees"

        # Add reviewers
        reviewers_data = {"reviewers": ["thejaptime"]}
        review_response = requests.post(review_url, headers=headers, json=reviewers_data)
        if review_response.status_code != 201:
            print(f"❌ Failed to add reviewers: {review_response.status_code}")
            print(f"Review response: {review_response.text}")

        # Add assignees
        assignees_data = {"assignees": ["tachingers"]}
        assign_response = requests.post(assign_url, headers=headers, json=assignees_data)
        print(f"Assignee response status: {assign_response.status_code}")
        if assign_response.status_code != 201:
            print(f"❌ Failed to add assignees: {assign_response.status_code}")
            print(f"Assign response: {assign_response.text}")

        if review_response.status_code == 201 and assign_response.status_code == 201:
            print("✅ Reviewers and assignees added successfully")
        else:
            print("❌ Failed to add reviewers or assignees")
    else:
        print(f"❌ Failed to create PR: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pull_request_trigger.py <head_branch> <base_branch>")
        sys.exit(1)

    head_branch = sys.argv[1]
    base_branch = sys.argv[2]
    create_pr(head_branch, base_branch)