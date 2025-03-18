import os
import json
import requests

# Get environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
REPO = os.getenv("GITHUB_REPOSITORY")

# Get PR number from event data
with open(os.getenv('GITHUB_EVENT_PATH')) as f:
    event_data = json.load(f)
PR_NUMBER = event_data['pull_request']['number']

# Get PR details from GitHub
headers = {"Authorization": f"token {GITHUB_TOKEN}"}
url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
response = requests.get(url, headers=headers)

if response.status_code != 200:
    raise Exception(f"Failed to fetch PR data: {response.status_code}, {response.text}")

pr_data = response.json()
title = pr_data["title"]
body = pr_data["body"]

# Use Together API to generate release note
prompt = f"Generate a release note based on this PR:\nTitle: {title}\nDescription: {body}"
api_url = "https://api.together.xyz/v1/chat/completions"
payload = {
    "model": "deepseek-ai/DeepSeek-R1",
    "messages": [{"role": "system", "content": prompt}]
}
headers = {
    "Authorization": f"Bearer {TOGETHER_API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(api_url, headers=headers, json=payload)

if response.status_code != 200:
    raise Exception(f"Failed to generate release note: {response.status_code}, {response.text}")

release_note = response.json()["choices"][0]["message"]["content"]

# Create a GitHub release
release_url = f"https://api.github.com/repos/{REPO}/releases"
release_data = {
    "tag_name": f"release-{PR_NUMBER}",
    "name": f"Release {PR_NUMBER}",
    "body": release_note,
    "draft": False,
    "prerelease": False
}
release_response = requests.post(release_url, headers=headers, json=release_data)

if release_response.status_code != 201:
    raise Exception(f"Failed to create release: {release_response.status_code}, {release_response.text}")

print("✅ Release note created successfully!")
