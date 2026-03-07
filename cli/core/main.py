import sys
from pathlib import Path
from InquirerPy import prompt

# Add the parent directory (project root) to the Python path
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

# NOW you can import services
from services import generic_api

"""
Entry point for the Media Management CLI.

This module handles the main user flow, dynamic service selection, 
and orchestration between the UI and the generic API methods.
"""

class UserInterface:
    """Handles terminal-based user interactions."""

    @staticmethod
    def media_type_dialog() -> str:
        """
        Displays a fuzzy-search dialog to select the type of media to process.

        Scans the 'services' directory for available media providers.

        Returns:
            str: The name of the selected media type (folder name).
        """
        services_path = Path(__file__).parent.parent / "services"
        # Filters directories and ignores private folders like __pycache__
        service_folder_names = [
            f.name for f in services_path.iterdir() 
            if f.is_dir() and not f.name.startswith(("_", "generic"))
        ]

        media_type_choice = [
            {
                "type": "fuzzy",
                "name": "media_type",
                "message": "What type of media do you want to add/edit?",
                "choices": service_folder_names,
            }
        ]
        result = prompt(media_type_choice)

        return result["media_type"]


def main():
    """
    Orchestrates the media search and selection workflow.
    
    1. Prompts for media type.
    2. Dynamically loads the corresponding API.
    3. Fetches, cleans, and prompts for a specific entry.
    """
    media_type = UserInterface.media_type_dialog()

    # 1. Fetch the API module once
    api = generic_api.get_service_api(media_type)

    # Check for error dictionary (Standard project pattern)
    if isinstance(api, dict) and "error" in api:
        print(f"❌ Error: {api['error']}")
        return

    media_name = input(f"Search name for {media_type}: ").strip()
    if not media_name:
        print("⚠️ Search name cannot be empty.")
        return

    # 2. Fetch raw data passing the api object
    raw_data = generic_api.media_fetch(api, media_name)
    if isinstance(raw_data, dict) and "error" in raw_data:
        print(f"❌ Fetch Error: {raw_data['error']}")
        return

    # 3. Clean and filter data
    media_data = generic_api.media_clean_up(api, raw_data)
    if isinstance(media_data, dict) and "error" in media_data:
        print(f"❌ Cleanup Error: {media_data['error']}")
        return

    # 4. User selection from results
    chosen_entry = generic_api.entry_choice(api, media_data)
    if isinstance(chosen_entry, dict) and "error" in chosen_entry:
        print(f"❌ Selection Error: {chosen_entry['error']}")
        return

if __name__ == "__main__":
    main()