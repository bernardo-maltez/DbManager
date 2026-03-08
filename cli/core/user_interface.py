from pathlib import Path
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

"""
Handles terminal-based user interactions.
Provides specialized dialogs for selecting media types and entering user metadata.
"""

def media_type_dialog() -> str:
    """
    Displays a fuzzy-search dialog to select the type of media to process.
    Scans the 'services' directory to find available media providers dynamically.

    Returns:
        str: The name of the selected media type folder (e.g., 'anime', 'manga').
    """
    # Navigate to the services directory relative to this file
    services_path = Path(__file__).parent.parent / "services"
    
    # Filter directories: ignores __pycache__, private folders, and the generic template
    service_folder_names = [
        f.name for f in services_path.iterdir() 
        if f.is_dir() and not f.name.startswith(("_", "generic"))
    ]

    media_type_choice = inquirer.fuzzy(
        message="What type of media do you want to interact with?",
        choices=service_folder_names
    ).execute()

    return media_type_choice

def media_status_dialog(media_status_options: list) -> str:
    """
    Prompts the user to select a status from a list of valid schema options.

    Args:
        media_status_options (list): A list of strings (e.g., ["Watching", "Completed"]).

    Returns:
        str: The selected status string.
    """
    media_status_choice = inquirer.fuzzy(
        message="What is the media status?",
        choices=media_status_options
    ).execute()

    return media_status_choice

def media_score_dialog() -> float:
    """
    Prompts the user for a numerical score.

    Returns:
        float: The user's score, allowing for decimals.
    """
    media_score_choice = inquirer.number(
        message="What's your score for this media? (0-5)",
        min_allowed=0,
        max_allowed=5,
        float_allowed=True
    ).execute()
 
    return media_score_choice

def media_times_dialog() -> int:
    """
    Prompts the user for the number of times the media has been consumed.

    Returns:
        int: Total consumption count.
    """
    media_times_choice = inquirer.number(
        message="How many times have you consumed this media?",
        min_allowed=1,
        float_allowed=False
    ).execute()
 
    return media_times_choice

def media_thougths_dialog() -> str:
    """
    Captures free-text thoughts from the user.

    Returns:
        str or None: The user's text input, or None if the input was left empty.
    """
    media_thougths = inquirer.text(
        message="Any thoughts?"
    ).execute()

    # Normalize empty input to None for cleaner JSON storage
    if media_thougths.strip() == "":
        media_thougths = None

    return media_thougths