import importlib

"""
Orchestration module for cross-media services.

This module provides a generic interface to dynamically load service providers 
(Anime, Manga, etc.) and execute fetching, cleaning, and selection operations 
without direct coupling to specific implementations.
"""

def get_service_api(media_type: str):
    """
    Dynamically loads the API module for a specific media type.

    Args:
        media_type (str): The name of the service (e.g., 'Anime', 'Manga').

    Returns:
        module: The loaded Python module if found.
        dict: A dictionary containing an 'error' key if the module is missing.
    """
    try:
        module_path = f"services.{media_type.lower()}.api"
        return importlib.import_module(module_path)
    except ImportError:
        return {"error": f"API module for '{media_type}' not found."}


def media_fetch(api, name: str) -> dict:
    """
    Executes a raw data search through the provided API provider.

    Args:
        api (module): The dynamically loaded API module.
        name (str): The name of the media to search for.

    Returns:
        dict: The raw data returned by the API or an attribute error message.
    """
    try:
        return api.run_fetch(name)
    except AttributeError:
        return {"error": f"Method 'run_fetch' not implemented in {api.__name__}"}


def media_clean_up(api, raw_data: dict) -> list:
    """
    Processes and filters raw API data into a simplified list format.

    Args:
        api (module): The dynamically loaded API module.
        raw_data (dict): The raw data dictionary from the fetch stage.

    Returns:
        list: A list of processed entries ready for selection.
        dict: An error dictionary if the method is missing.
    """
    try:
        return api.run_clean_up(raw_data)
    except AttributeError:
        return {"error": f"Method 'run_clean_up' not implemented in {api.__name__}"}


def entry_choice(api, cleaned_data: list) -> dict:
    """
    Interface for the user to choose a specific entry from the processed list.

    Args:
        api (module): The dynamically loaded API module.
        cleaned_data (list): The filtered and cleaned list of media entries.

    Returns:
        dict: The entry selected by the user or an error message.
    """
    try:
        return api.run_choice(cleaned_data)
    except AttributeError:
        return {"error": f"Method 'run_choice' not implemented in {api.__name__}"}