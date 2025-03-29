from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

def get_openai_client():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set. Please add it to your .env file.")

    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

def generate_pr_body(changes: List[Dict[str, str]]) -> str:
    """
    Generate a pull request body based on file changes.

    Args:
        changes: List of dictionaries containing file changes with keys:
                - file_path: Path to the changed file
                - change_type: Type of change (added, modified, deleted)
                - diff: The actual changes in the file

    Returns:
        str: Generated PR body

    Raises:
        ValueError: If the API key is not set
        Exception: If there's an error generating the PR body
    """
    try:
        client = get_openai_client()

        # Create a prompt that describes the changes
        changes_description = "\n".join([
            f"- {change['file_path']} ({change['change_type']})"
            for change in changes
        ])

        prompt = f"""Please generate a professional pull request description based on the following changes:

{changes_description}

The PR description should include:
1. A brief summary of the changes
2. The purpose/motivation for these changes
3. Any important implementation details
4. Any testing that was done
5. Any breaking changes or dependencies

Please format the response in markdown."""

        completion = client.chat.completions.create(
            model="google/gemini-2.5-pro-exp-03-25:free",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        if not completion or not completion.choices:
            raise Exception("No response received from the API")

        return completion.choices[0].message.content

    except Exception as e:
        print(f"Error generating PR body: {str(e)}")
        # Return a basic PR body as fallback
        return f"""# Pull Request

## Changes
{changes_description}

## Description
This PR includes the following changes:
{changes_description}

Please review the changes and provide feedback."""

# Example usage
if __name__ == "__main__":
    sample_changes = [
        {
            "file_path": "api/generate_pr_body.py",
            "change_type": "added",
            "diff": "Added new function to generate PR body"
        }
    ]
    pr_body = generate_pr_body(sample_changes)
    print(pr_body)