import requests
from InquirerPy import prompt
from InquirerPy.base.control import Choice

"""
AniList API Service Provider.

This module handles GraphQL requests to AniList, data extraction, 
and user selection specifically for Anime media types.
"""

ANILIST_URL = 'https://graphql.anilist.co'

# --- Specific Methods ---

def fetch_data(url: str, headers: dict = None, payload: dict = None) -> dict:
    """
    Performs a generic HTTP request and handles the response.

    Args:
        url (str): The destination URL.
        headers (dict, optional): HTTP headers. Defaults to None.
        payload (dict, optional): JSON payload for POST requests. Defaults to None.

    Returns:
        dict: The JSON response from the server or an error dictionary.
    """
    try:
        if payload:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
        else:
            response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        return {'error': f"HTTP {response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {'error': f"Connection failed: {str(e)}"}


def anilist_data(name: str) -> dict:
    """
    Queries the AniList GraphQL API for anime search results.

    Args:
        name (str): The search query (anime title).

    Returns:
        dict: Raw GraphQL response or error dictionary.
    """
    query = """
        query ($query: String, $format: MediaType, $page: Int, $perpage: Int) {
            Page (page: $page, perPage: $perpage) {
                media (search: $query, type: $format) {
                    title {
                        romaji
                        english
                    }
                    type
                    genres
                    countryOfOrigin
                    startDate {
                        year
                        month
                        day
                    }
                    duration
                    episodes
                    chapters
                }
            }
        }
    """
    variables = {
        'query': name,
        'format': "ANIME",
        'page': 1,
        'perpage': 5  # Increased slightly for better fuzzy choice
    }
    return fetch_data(ANILIST_URL, payload={'query': query, 'variables': variables})


# --- Generic Methods (Used by Orchestrator) ---

def run_fetch(name: str) -> dict:
    """
    Standardized entry point for the fetching stage.
    """
    return anilist_data(name)


def run_clean_up(raw_data: dict) -> list:
    """
    Extracts the list of media entries from raw AniList JSON.

    Args:
        raw_data (dict): Raw data from anilist_data.

    Returns:
        list: A list of media dictionaries.
    """
    return raw_data.get('data', {}).get('Page', {}).get('media', [])


def run_choice(entries: list):
    """
    Prompt the user to select one anime from the list of results.

    Args:
        entries (list): List of cleaned media entries.

    Returns:
        dict: The full dictionary of the selected entry, or None.
    """
    if not entries:
        return {"error": "No entries found to choose from."}

    formatted_choices = []
    
    for index, entry in enumerate(entries):
        title_data = entry.get('title', {})
        # AniList specific title logic
        title_text = title_data.get('english') or title_data.get('romaji') or 'Unknown Title'
        
        # Extract year from startDate dict
        start_date = entry.get('startDate', {})
        year = start_date.get('year') if start_date else "????"
        
        display_name = f"{title_text} ({year})"
        
        # We pass the actual entry dict as the value
        formatted_choices.append(Choice(value=entry, name=display_name))
    
    formatted_choices.append(Choice(value=None, name="Cancel selection"))

    questions = [
        {
            "type": "fuzzy",
            "name": "selected_entry",
            "message": "Which entry do you want?",
            "choices": formatted_choices,
        }
    ]
    
    result = prompt(questions)
    return result.get("selected_entry")