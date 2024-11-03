import requests
import csv
from getpass import getpass
import time

# GitHub API credentials and token setup for pushing to GitHub
token = getpass('Enter your GitHub personal access token:')
headers = {"Authorization": f"token {token}"}

# Set your GitHub username and repository name here
GITHUB_USERNAME = "Abimanyu-A-J"
GITHUB_REPO_NAME = "TDSProj1"

# Clone the repository and change directory to it
!git clone https://{token}@github.com/{GITHUB_USERNAME}/{GITHUB_REPO_NAME}.git
%cd {GITHUB_REPO_NAME}

# Helper functions for GitHub API
def get_users():
    users = []
    page = 1
    while True:
        url = f"https://api.github.com/search/users?q=location:Melbourne+followers:>100&per_page=100&page={page}"
        response = requests.get(url, headers=headers)

        # Check for API rate limiting
        if response.status_code == 403:
            print("Rate limit reached. Waiting for 60 seconds before retrying...")
            time.sleep(60)
            continue

        data = response.json()
        users.extend(data["items"])

        # Break if less than 100 results are returned, indicating the last page
        if len(data["items"]) < 100:
            break

        page += 1
        time.sleep(1)  # Add delay to avoid hitting rate limits too quickly

    return users

def get_user_details(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers=headers)
    return response.json()

def get_user_repos(username):
    url = f"https://api.github.com/users/{username}/repos?sort=pushed"
    response = requests.get(url, headers=headers)
    return response.json()[:500]

def clean_company(company):
    if company:
        company = company.lstrip('@').strip().upper()
    return company

# Writing to CSV files
def write_users_csv(users):
    with open("users.csv", "w", newline="") as user_file:
        writer = csv.writer(user_file)
        writer.writerow(["login", "name", "company", "location", "email", "hireable", "bio", "public_repos", "followers", "following", "created_at"])

        for user in users:
            details = get_user_details(user["login"])
            writer.writerow([
                details["login"],
                details["name"] or "",
                clean_company(details["company"]),
                details["location"] or "",
                details["email"] or "",
                details["hireable"],
                details["bio"] or "",
                details["public_repos"],
                details["followers"],
                details["following"],
                details["created_at"]
            ])

def write_repos_csv(users):
    with open("repositories.csv", "w", newline="") as repo_file:
        writer = csv.writer(repo_file)
        writer.writerow(["login", "full_name", "created_at", "stargazers_count", "watchers_count", "language", "has_projects", "has_wiki", "license_name"])

        for user in users:
            for repo in get_user_repos(user["login"]):
                writer.writerow([
                    user["login"],
                    repo["full_name"],
                    repo["created_at"],
                    repo["stargazers_count"],
                    repo["watchers_count"],
                    repo["language"] or "",
                    repo["has_projects"],
                    repo["has_wiki"],
                    repo["license"]["key"] if repo["license"] else ""
                ])

# Fetch and save user and repository data
users = get_users()
print(f"Total users fetched: {len(users)}")  # Should be around 335
write_users_csv(users)
write_repos_csv(users)

# Git configuration and pushing changes
!git config --global user.email "23f2000919@ds.study.iitm.ac.in"
!git config --global user.name "Abimanyu-A-J"

def push_to_github():
    # Commit and push changes
    !git add users.csv repositories.csv README.md
    !git commit -m "Update users.csv, repositories.csv, and README.md with latest data"
    !git push https://{token}@github.com/{GITHUB_USERNAME}/{GITHUB_REPO_NAME}.git

# Execute the push function to upload changes
push_to_github()
