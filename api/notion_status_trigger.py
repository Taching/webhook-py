import os
import sys
from dotenv import load_dotenv
import requests

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("DATABASE_ID")

def update_status(page_title, headers, new_status, github):
    """Update the status of a page"""
    url = f"https://api.notion.com/v1/pages/{page_title}"

    # First get the current page to get the status options
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"Failed to get page: {res.status_code}")
        print(f"Response: {res.text}")
        return False

    # Get the current status
    page_data = res.json()
    current_status = page_data.get('properties', {}).get('Status', {}).get('status', {}).get('name')
    print(f"\nCurrent status: {current_status}")

    # Get database schema to find available status options
    res = requests.get(f"https://api.notion.com/v1/databases/{DATABASE_ID}", headers=headers)
    if res.status_code != 200:
        print(f"Failed to get database schema: {res.status_code}")
        print(f"Response: {res.text}")
        return False

    # Get status options from database schema
    database = res.json()

    # Debug: Print all available properties
    print("\nAvailable database properties:")
    for prop_name, prop_data in database.get('properties', {}).items():
        print(f"- {prop_name} (type: {prop_data.get('type')})")

    status_config = database.get('properties', {}).get('Status', {}).get('status', {})
    status_options = status_config.get('options', [])

    # Print available status options
    print("\nAvailable status options:")
    for opt in status_options:
        print(f"- {opt.get('name')}")

    # Find the "Done" status option
    done_option = next((opt for opt in status_options if opt.get('name') == new_status), None)
    if not done_option:
        print(f"\nCould not find '{new_status}' status option. Please use one of the available options above.")
        return False

    # Update the page with the new status and GitHub field
    update_data = {
        "properties": {
            "Status": {
                "status": {
                    "name": new_status
                }
            }
        }
    }

    # Add GitHub field if provided
    if github:
        # Try different possible property names for GitHub
        github_property_name = None
        for prop_name, prop_data in database.get('properties', {}).items():
            if prop_data.get('type') == 'url' and 'github' in prop_name.lower():
                github_property_name = prop_name
                break

        if github_property_name:
            update_data["properties"][github_property_name] = {
                "url": github
            }
        else:
            print("Warning: Could not find GitHub URL property in database")

    res = requests.patch(url, headers=headers, json=update_data)
    if res.status_code == 200:
        print("Status and GitHub field updated successfully!")
        return True
    else:
        print(f"Failed to update status: {res.status_code}")
        print(f"Response: {res.text}")
        return False

if len(sys.argv) < 2:
    print("Usage: python slack_trigger.py <search_title> new_status [github_url]")
    sys.exit(1)

SEARCH_TITLE = sys.argv[1]
NEW_STATUS = sys.argv[2]
GITHUB_URL = sys.argv[3] if len(sys.argv) > 3 else None

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

# First verify the API key
print("Verifying API key...")
res = requests.get("https://api.notion.com/v1/users/me", headers=headers)
if res.status_code != 200:
    print(f"API Key verification failed: {res.status_code}")
    print(f"Response: {res.text}")
    exit(1)

print("API Key is valid! Now searching for tickets...")

# Search in the database
res = requests.post(f"https://api.notion.com/v1/databases/{DATABASE_ID}/query",
    headers=headers,
    json={
        "filter": {
            "property": "Task name",
            "title": {
                "contains": SEARCH_TITLE
            }
        }
    }
)

if res.status_code == 200:
    data = res.json()
    results = data.get('results', [])
    if not results:
        print(f"\nNo results found for '{SEARCH_TITLE}'")
    else:
        print(f"\nSearch results for '{SEARCH_TITLE}':")
        for page in results:
            properties = page.get('properties', {})
            print(f"\nTicket ID: {page.get('id')}")

            # Get title
            title = properties.get('Task name', {}).get('title', [])
            title_text = title[0].get('plain_text', 'No title') if title else 'No title'
            print(f"Title: {title_text}")

            # Get status
            status = properties.get('Status', {}).get('status', {})
            print(f"Status: {status.get('name', 'No status')}")

            # Get assignee
            assignees = properties.get('Assignee', {}).get('people', [])
            assignee_name = assignees[0].get('name', 'No assignee') if assignees else 'No assignee'
            print(f"Assignee: {assignee_name}")

            # Get due date
            due = properties.get('Due', {})
            if due and due.get('date'):
                print(f"Due: {due['date'].get('start', 'No due date')}")
            else:
                print("Due: No due date")

            # Update status if requested
            if NEW_STATUS:
                print(f"\nUpdating status to {NEW_STATUS}...")
                update_status(page.get('id'), headers, NEW_STATUS, GITHUB_URL)
else:
    print(f"Failed to search database: {res.status_code}")
    print(f"Response: {res.text}")


