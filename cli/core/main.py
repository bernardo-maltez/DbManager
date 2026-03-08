import sys
from pathlib import Path

# Absolute path resolution to ensure the root directory is in the Python path
# This allows 'import services' and 'import core' to work regardless of execution context
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

from services import generic_api
from core import user_interface as ui

"""
Entry point for the Media Management CLI.

This module handles the main user flow, dynamic service selection, 
and orchestration between the UI and the generic API methods. 
It follows a linear pipeline: Load -> Fetch -> Clean -> Choose -> Process.
"""

def main():
    """
    Orchestrates the media search and selection workflow.
    
    Workflow:
    1. Prompt user for media category (Anime, Manga, etc.).
    2. Dynamically load the service provider module via the orchestrator.
    3. Capture search keywords from user.
    4. Fetch data from the provider's remote source.
    5. Clean and format the raw results into a selectable list.
    6. Present a selection UI to the user.
    7. Process the selected entry into a schema-compliant dictionary.
    """
    
    # 0. Identify the media domain
    media_type = ui.media_type_dialog()

    # 1. Dynamically load the API module
    api = generic_api.get_service_api(media_type)
    if isinstance(api, dict) and "error" in api:
        print(f"❌ {api['error']}")
        return

    # 2. Capture search query
    media_name = input(f"Search name for {media_type}: ").strip()
    if not media_name:
        print("❌ Search name cannot be empty.")
        return

    # 3. Fetch raw data using the dynamic provider
    print(f"🔍 Searching for '{media_name}'...")
    raw_data = generic_api.media_fetch(api, media_name)
    if isinstance(raw_data, dict) and "error" in raw_data:
        print(f"❌ Fetch Error: {raw_data['error']}")
        return

    # 4. Filter and clean API response
    media_data = generic_api.media_clean_up(api, raw_data)
    if isinstance(media_data, dict) and "error" in media_data:
        print(f"❌ Cleanup Error: {media_data['error']}")
        return 

    # 5. User selection from list of results
    chosen_entry = generic_api.entry_choice(api, media_data)
    if chosen_entry is None:
        print("🚫 Selection cancelled by user.")
        return
    if isinstance(chosen_entry, dict) and "error" in chosen_entry:
        print(f"❌ Selection Error: {chosen_entry['error']}")
        return
    
    # 6. Transform selection into finalized schema entry
    # This usually triggers user input prompts for scores/thoughts
    processed_entry = generic_api.media_process(api, chosen_entry)
    if isinstance(processed_entry, dict) and "error" in processed_entry:
        print(f"❌ Processing Error: {processed_entry['error']}")
        return

    print("✨ Processed Entry successfully created!")
    # NEXT STEP: Would you like to implement the save_to_json logic here?

if __name__ == "__main__":
    main()