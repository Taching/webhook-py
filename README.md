# Notion Status Trigger

A Python script that allows you to search for Notion database entries and update their status through the command line.

## Features

- Search for tasks in a Notion database by title
- Display detailed information about matching tasks including:
  - Task ID
  - Title
  - Current Status
  - Assignee
  - Due Date
- Update the status of tasks to a specified value
- Verify available status options in the database
- API key validation

## Prerequisites

- Python 3.x
- Notion API Key
- Notion Database ID
- Required Python packages:
  - `python-dotenv`
  - `requests`

## Setup

1. Clone this repository
2. Install the required packages:
   ```bash
   pip install python-dotenv requests
   ```
3. Create a `.env` file in the root directory with the following variables:
   ```
   NOTION_API_KEY=your_notion_api_key
   DATABASE_ID=your_database_id
   ```

## Usage

The script can be run from the command line with the following syntax:

```bash
python api/notion_status_trigger.py <search_title> <new_status>
```

### Parameters

- `search_title`: The text to search for in task titles
- `new_status`: The new status to set for matching tasks

### Example

```bash
python api/notion_status_trigger.py "Project Review" "Done"
```

This will:

1. Search for tasks containing "Project Review" in their title
2. Display detailed information about matching tasks
3. Update the status of matching tasks to "Done"

## Output

The script will provide the following information:

- API key verification status
- Search results including:
  - Task ID
  - Title
  - Current Status
  - Assignee
  - Due Date
- Available status options in the database
- Status update confirmation

## Error Handling

The script includes error handling for:

- Invalid API key
- Database access issues
- Invalid status values
- Missing search results

## Notes

- The script uses the Notion API version 2022-06-28
- Status updates will only occur if the specified status exists in the database's status options
- The script will display all available status options if an invalid status is provided
