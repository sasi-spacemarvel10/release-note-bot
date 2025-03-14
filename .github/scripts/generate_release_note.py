import os
import json
import requests
import openai

# Get environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPO = os.getenv("GITHUB_REPOSITORY")

# Get PR number from event data
with open(os.getenv('GITHUB_EVENT_PATH')) as f:
    event_data = json.load(f)
PR_NUMBER = event_data['pull_request']['number']

# Set OpenAI API Key
import openai
openai.api_key = OPENAI_API_KEY

# Get PR details from GitHub
headers = {"Authorization": f"token {GITHUB_TOKEN}"}
url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
response = requests.get(url, headers=headers)

if response.status_code != 200:
    raise Exception(f"Failed to fetch PR data: {response.status_code}, {response.text}")

pr_data = response.json()
title = pr_data["title"]
body = pr_data["body"]

# Use OpenAI to generate release note
prompt = f"Generate a release note based on this PR:\nTitle: {title}\nDescription: {body}"
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "system", "content": prompt}]
)
release_note = response["choices"][0]["message"]["content"]

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
