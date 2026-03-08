import requests
import sys
import uuid
from datetime import datetime
from pathlib import Path
from InquirerPy import inquirer

# Path setup to ensure core and services are discoverable
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

from core import schemas
from core import user_interface as ui

"""
AniList API Service Provider.

This module handles GraphQL requests to AniList, data extraction, 
and user selection specifically for Anime media types.
"""

ANILIST_URL = 'https://graphql.anilist.co'

def fetch_data(url: str, headers: dict = None, payload: dict = None) -> dict:
    """
    Performs a generic HTTP request and handles the response.

    Args:
        url (str): The destination URL.
        headers (dict, optional): HTTP headers. Defaults to None.
        payload (dict, optional): JSON payload for POST requests. Defaults to None.

    Returns:
        dict: The JSON response from the server or an error dictionary containing 
              the exception or HTTP status code.
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


def user_input(media_status_list: list, total_episodes: int) -> dict:
    """
    Orchestrates the terminal UI dialogs to collect user-specific data for an entry.

    Args:
        media_status_list (list): Allowed strings for user status (from schema).
        total_episodes (int): Max episodes allowed for the 'current_episode' input.

    Returns:
        dict: A collection of user responses including status, episodes, 
              watch count, score, and personal thoughts.
    """
    status = ui.media_status_dialog(media_status_list)
    
    # Handle cases where total_episodes might be None from API
    max_ep = total_episodes if total_episodes else 9999
    
    episodes = inquirer.number(
        message="How many episodes have you seen?",
        min_allowed=0,
        max_allowed=max_ep
    ).execute()
    
    times = ui.media_times_dialog() 
    score = ui.media_score_dialog()
    thoughts = ui.media_thougths_dialog()

    return {
        "status": status,
        "current_episode": episodes,
        "times_watched": times,
        "score": score,
        "thoughts": thoughts
    }

# --- Generic Methods (Used by Orchestrator) ---

def run_fetch(name: str) -> dict:
    """
    Queries the AniList GraphQL API for anime search results.

    Args:
        name (str): The search query (anime title).

    Returns:
        dict: Raw GraphQL response containing a Page of media results.
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
        'perpage': 5
    }
    return fetch_data(ANILIST_URL, payload={'query': query, 'variables': variables})


def run_clean_up(raw_data: dict) -> list:
    """
    Parses the raw GraphQL response to extract the media list.

    Args:
        raw_data (dict): The dictionary returned by run_fetch.

    Returns:
        list: A list of media dictionaries. Returns empty list if data is missing.
    """
    return raw_data.get('data', {}).get('Page', {}).get('media', [])


def run_process_entry(entry_data: dict) -> dict:
    """
    Maps raw API data and user input into the standardized application schema.

    Args:
        entry_data (dict): The raw media dictionary selected by the user.

    Returns:
        dict: A fully populated dictionary ready for JSON database insertion, 
              matching the application's video schema.
    """
    # NOTE: Use the template getter here, not the full metadata schema
    processed_entry = schemas.get_full_schema_for("anime") 
    
    # Get the rules/metadata separately just for the status options
    api_rules = schemas.get_full_schema_for("anime")

    titles = entry_data.get('title', {})
    start_date = entry_data.get('startDate', {})
    
    entry_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Extract options from the metadata rules
    status_options = api_rules["userStatus"]["options"]
    user_input_data = user_input(status_options, entry_data.get('episodes'))

    processed_entry.update({
        "id": str(uuid.uuid4())[:8],
        "entryDate": entry_timestamp,
        "mediaTitle": titles.get('romaji'),
        "mediaTitleAlternatives": [titles.get('english')] if titles.get('english') else [],
        "mediaGenres": entry_data.get('genres', []),
        "mediaReleaseDate": f"{start_date.get('year')}-{start_date.get('month')}-{start_date.get('day')}",
        "mediaCountry": entry_data.get('countryOfOrigin'),
        "mediaTotalEpisodes": entry_data.get('episodes'),
        "userCurrentEpisode": user_input_data['current_episode'],
        "userTimesWatched": user_input_data['times_watched'],
        "userStatus": user_input_data['status'],
        "userScore": user_input_data['score'],
        "userThoughts": user_input_data['thoughts']
    })
    
    return processed_entry