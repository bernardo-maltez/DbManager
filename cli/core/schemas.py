"""
Central repository for all data structures and validation schemas used in the application.
"""

# Base fields shared by all media types (Anime, Manga, Games, etc.)
METADATA_COMMON_FIELDS = {
    "id": { "type": "string", "length": 8 },
    "entryDate": { "type": "datetime", "format": "YYYY-MM-DD HH:MM:SS" },      
    "mediaTitle": { "type": "string", "min": 1 }, 
    "mediaTitleAlternatives": { "type": "array", "items": "string" },     
    "mediaGenres": { "type": "array", "items": "string" },      
    "mediaReleaseDate": { "type": "datetime", "format": "YYYY-MM-DD" },      
    "mediaCountry": { "type": "string", "min": 1 },
    "userScore": { "type": "float", "min": 0, "max": 10 },
    "userThoughts": { "type": "string", "min": 0 }
}

# Extension fields unique to specific media categories
METADATA_SPECIFIC_FIELDS = {
    "ANIME": {
        "userStatus": { 
            "type": "string", 
            "options": ["Watching", "Watched", "Planning", "Dropped"]
        },
        "mediaTotalEpisodes": { "type": "float", "min": 0},
        "userCurrentEpisode": { "type": "float", "min": 0},
        "userTimesWatched": { "type": "int", "min": 0}
    }
}

# UI Configuration for column display based on status
SHOW_COLUMNS = {
    "ANIME": {
        "showColumns":  {
            "default": ["mediaTitle", "mediaReleaseDate", "userScore", "userThoughts"],
            "Watched": ["mediaTitle", "mediaTotalEpisodes", "userScore", "userThoughts"],
            "Watching": ["mediaTitle", "userCurrentEpisode", "mediaTotalEpisodes"]
        }
    }
}

def get_full_schema_for(media_type: str) -> dict:
    """
    Combines common metadata fields with media-specific fields.

    Args:
        media_type (str): The category (e.g., 'ANIME').

    Returns:
        dict: A merged dictionary containing the complete validation schema.
    """
    common = METADATA_COMMON_FIELDS
    specific = METADATA_SPECIFIC_FIELDS.get(media_type.upper())

    base_schema = {**common, **specific}
    nullified_schema = {key: None for key in base_schema}
    
    return nullified_schema

def get_show_columns(media_type: str) -> dict:
    """
    Retrieves the UI column configuration for a specific media type.

    Args:
        media_type (str): The category (e.g., 'ANIME').

    Returns:
        dict: The display configuration for various user statuses.
    """
    # Return the inner 'showColumns' dict directly
    data = SHOW_COLUMNS.get(media_type.upper(), {})
    return data.get("showColumns", {})