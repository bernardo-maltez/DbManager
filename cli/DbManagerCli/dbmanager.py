import datetime
import os
from typing import List, Dict, Any
import pandas as pd
import json
from InquirerPy import prompt
from InquirerPy.base.control import Choice

import DbManagerCli.search as search
import settings

class MediaTypes:
    ANIME = "ANIME"
    MANGA = "MANGA"
    MOVIE = "MOVIE"

class MediaStatus:
    ANIME = ["Watching", "Watched", "Paused", "Dropped", "PlanToWatch"]
    MANGA = ["Reading", "Read", "Paused", "Dropped", "PlanToRead"]
    MOVIE = ["Watched", "PlanToWatch"]

class UserInterface:
    @staticmethod
    def media_type_choice() -> str:
        choices = [
            Choice(MediaTypes.ANIME, name="Anime"),
            Choice(MediaTypes.MANGA, name="Manga"),
            Choice(MediaTypes.MOVIE, name="Movie"),
            Choice("Cancel", name="Cancel")
        ]
        
        questions = [
            {
                "type": "fuzzy",
                "name": "media_type",
                "message": "What type of media do you want to add/edit?",
                "choices": choices,
            }
        ]
        
        result = prompt(questions)
        return result["media_type"]

    @staticmethod
    @staticmethod
    def entry_choice(entries: List[Dict[str, Any]], media_type: str) -> int:
        choices = []
        
        for entry in entries:
            if media_type in [MediaTypes.ANIME, MediaTypes.MANGA]:
                title = entry.get('title', {})
                if isinstance(title, dict):
                    title_text = title.get('english') or title.get('originalTitle') or 'Unknown Title'
                else:
                    title_text = str(title)
                release_date = entry.get('releaseDate', 'Unknown Date')
                entry_text = f"{title_text} -- {release_date[:4] if release_date else 'Unknown Year'}"
            elif media_type == MediaTypes.MOVIE:
                title = entry.get('title', {})
                if isinstance(title, dict):
                    title_text = title.get('originalTitle') or title.get('english') or 'Unknown Title'
                else:
                    title_text = str(title)
                release_date = entry.get('releaseDate', 'Unknown Date')
                entry_text = f"{title_text} -- {release_date[:4] if release_date else 'Unknown Year'}"
            else:
                entry_text = "Unknown Entry"
            
            choices.append(Choice(value=entries.index(entry), name=entry_text))
        
        choices.append(Choice(value=None, name="None"))

        questions = [
            {
                "type": "fuzzy",
                "name": "entry",
                "message": "Which entry do you want?",
                "choices": choices,
            }
        ]
        
        result = prompt(questions)
        return result["entry"]

    @staticmethod
    def media_status_choice(media_type: str) -> str:
        choices = [Choice(status) for status in getattr(MediaStatus, media_type)]
        
        questions = [
            {
                "type": "list",
                "name": "status",
                "message": "What is the media status?",
                "choices": choices,
            }
        ]
        
        result = prompt(questions)
        return result["status"]

    @staticmethod
    def score_choice() -> str:
        choices = ["Favorite", "Excellent", "Nice", "Regular", "Bad", "Horrible"]
        
        questions = [
            {
                "type": "list",
                "name": "score",
                "message": "What is your score for this media?",
                "choices": choices,
            }
        ]
        
        result = prompt(questions)
        return result["score"]

    @staticmethod
    def edit_field_choice(entry: Dict[str, Any]) -> str:
        choices = [Choice(field) for field in entry.keys()]

        choices.append(Choice("Done", name="Finished Editing"))
        
        questions = [
            {
                "type": "fuzzy",
                "name": "field",
                "message": "Which field do you want to edit?",
                "choices": choices,
            }
        ]
        
        result = prompt(questions)
        return result["field"]

class DataProcessor:
    @staticmethod
    def process_entry(entry: Dict[str, Any], media_type: str, media_status: str) -> Dict[str, Any]:
        if media_type in [MediaTypes.ANIME, MediaTypes.MANGA]:
            return DataProcessor.process_anilist_entry(entry, media_type, media_status)
        elif media_type == MediaTypes.MOVIE:
            return DataProcessor.process_movie_entry(entry, media_status)
        else:
            raise ValueError(f"Invalid media type: {media_type}")

    @staticmethod
    def process_anilist_entry(entry: Dict[str, Any], media_type: str, media_status: str) -> Dict[str, Any]:
        processed_entry = {
            "title": {
                "originalTitle": entry["title"]["romaji"],
                "english": entry["title"]["english"] or entry["title"]["romaji"]
            },
            "releaseDate": f"{entry['startDate']['year']}-{entry['startDate']['month']}-{entry['startDate']['day']}",
            "countryOfOrigin": DataProcessor.country_fix(entry["countryOfOrigin"]),
            "genres": entry["genres"],
            "status": media_status,
            "thoughts": input("Any final thoughts?\n"),
            "entryDate": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if media_type == MediaTypes.ANIME:
            processed_entry["total_episodes"] = entry["episodes"]
            processed_entry["watched_episodes"] = DataProcessor.amount_input(entry["episodes"], media_status)
        elif media_type == MediaTypes.MANGA:
            processed_entry["total_chapters"] = entry["chapters"]
            processed_entry["read_chapters"] = DataProcessor.amount_input(entry["chapters"], media_status)

        if media_status not in ["PlanToWatch", "PlanToRead"]:
            processed_entry["score"] = UserInterface.score_choice()
            processed_entry["times_rewatched"] = int(input("How many times have you seen this? "))

        return processed_entry

    @staticmethod
    def process_movie_entry(entry: Dict[str, Any], media_status: str) -> Dict[str, Any]:
        movie_data = search.movie_data(entry["id"])
        
        processed_entry = {
            "title": {
                "originalTitle": movie_data["original_title"],
                "portuguese": input("Insira o título em português: ")
            },
            "releaseDate": movie_data["release_date"],
            "countryOfOrigin": [country["name"] for country in movie_data["production_countries"]],
            "genres": [genre["name"] for genre in movie_data["genres"]],
            "duration": movie_data["runtime"],
            "status": media_status,
            "thoughts": input("Any final thoughts?\n"),
            "entryDate": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if media_status != "PlanToWatch":
            processed_entry["score"] = UserInterface.score_choice()
            processed_entry["times_watched"] = int(input("How many times have you seen this? "))

        return processed_entry

    @staticmethod
    def amount_input(total: int, media_status: str) -> int:
        if media_status in ["PlanToWatch", "PlanToRead"]:
            return 0
        elif media_status in ["Watched", "Read"] and total is not None:
            return total

        while True:
            try:
                amount = int(input(f"How much have you seen? Total of {total}: " if total else "How much have you seen? "))
                if not total or 0 <= amount <= total:
                    return amount
                print(f'Please enter a value between 0 and {total}.')
            except ValueError:
                print("Please enter a valid numerical value!")

    @staticmethod
    def country_fix(country: str) -> str:
        country_map = {"JP": "Japan", "KR": "Korea", "CN": "China"}
        return country_map.get(country, country)

class DatabaseHandler:
    ANIME_PRESET = {"ANIME": [{"Watching": []}, {"Watched": []}, {"Paused": []}, {"Dropped": []}, {"PlanToWatch": []}]}
    MANGA_PRESET = {"MANGA": [{"Reading": []}, {"Read": []}, {"Paused": []}, {"Dropped": []}, {"PlanToRead": []}]}
    MOVIE_PRESET = {"MOVIE": [{"Watched": []}, {"PlanToWatch": []}]}

    @staticmethod
    def get_preset(media_type: str) -> Dict:
        return getattr(DatabaseHandler, f"{media_type}_PRESET")

    @staticmethod
    def db_load(db_path: str, media_type: str) -> Dict:
        folder_path = settings.folderPath
        os.makedirs(folder_path, exist_ok=True)
        os.chdir(folder_path)

        if not os.path.exists(db_path) or os.stat(db_path).st_size == 0:
            preset = DatabaseHandler.get_preset(media_type)
            with open(db_path, "w", encoding="utf-8") as file:
                json.dump(preset, file, indent=2, ensure_ascii=False)

        with open(db_path, "r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def db_entry_add(entry_data: Dict, db_data: Dict, media_type: str, media_status: str) -> Dict:
        for status_dict in db_data[media_type]:
            if media_status in status_dict:
                status_dict[media_status].append(entry_data)
                return db_data
        raise ValueError(f"Category with media_status {media_status} not found")

    @staticmethod
    def db_entry_update(entry_data: Dict, db_data: Dict, media_type: str, old_status: str, new_status: str) -> Dict:
        # Remove the entry from the old status
        for status_dict in db_data[media_type]:
            if old_status in status_dict:
                status_dict[old_status] = [entry for entry in status_dict[old_status] if entry['title'] != entry_data['title']]
        
        # Add the entry to the new status
        for status_dict in db_data[media_type]:
            if new_status in status_dict:
                status_dict[new_status].append(entry_data)
                break
        else:
            raise ValueError(f"Category with media_status {new_status} not found")

        return db_data

    @staticmethod
    def db_write(db_data: Dict, db_path: str) -> None:
        with open(db_path, "w", encoding="utf-8") as file:
            json.dump(db_data, file, indent=2, ensure_ascii=False)
        print("Successfully written to file")

def add_entry() -> None:
    media_type = UserInterface.media_type_choice()
    if media_type == "Cancel":
        return

    media_name = input("Please input the name of the desired media: ").strip()

    if media_type in [MediaTypes.ANIME, MediaTypes.MANGA]:
        media_data = search.anilist_data(media_name, media_type)["data"]["Page"]["media"]
    elif media_type == MediaTypes.MOVIE:
        media_data = search.movie_search(media_name)["results"]
    else:
        print("Invalid media type!")
        return

    if not media_data:
        print("Couldn't find the desired media!")
        return

    entry_index = UserInterface.entry_choice(media_data, media_type)
    if entry_index is None:
        return

    desired_entry = media_data[entry_index]
    media_status = UserInterface.media_status_choice(media_type)

    processed_data = DataProcessor.process_entry(desired_entry, media_type, media_status)

    db_file = f"{media_type.lower()}Db.json"
    db_path = os.path.join(settings.folderPath, db_file)
    db_data = DatabaseHandler.db_load(db_path, media_type)

    db_data = DatabaseHandler.db_entry_add(processed_data, db_data, media_type, media_status)

    DatabaseHandler.db_write(db_data, db_path)

def edit_entry() -> None:
    media_type = UserInterface.media_type_choice()
    if media_type == "Cancel":
        return

    # Load db
    db_file = f"{media_type.lower()}Db.json"
    db_path = os.path.join(settings.folderPath, db_file)
    db_data = DatabaseHandler.db_load(db_path, media_type)

    all_entries = []
    for status_dict in db_data[media_type]:
        for status, entries in status_dict.items():
            all_entries.extend(entries)

    if not all_entries:
        print("No entries found in the database.")
        return

    entry_index = UserInterface.entry_choice(all_entries, media_type)
    if entry_index is None:
        return

    entry_to_edit = all_entries[entry_index]
    old_status = entry_to_edit['status']

    while True:
        field_to_edit = UserInterface.edit_field_choice(entry_to_edit)
        if field_to_edit == "Done":
            break
        
        elif field_to_edit == "status":
            new_status = UserInterface.media_status_choice(media_type)
            entry_to_edit['status'] = new_status
        
        elif field_to_edit == "score":
            new_score = UserInterface.score_choice()
            entry_to_edit['score'] = new_score

        elif isinstance(entry_to_edit[field_to_edit], dict):
            sub_field = UserInterface.edit_field_choice(entry_to_edit[field_to_edit])
            entry_to_edit[field_to_edit][sub_field] = input(f"Enter new value for {field_to_edit}.{sub_field}: ")
        else:
            entry_to_edit[field_to_edit] = input(f"Enter new value for {field_to_edit}: ")

    if entry_to_edit['status'] == old_status:
        new_status = old_status
    
    entry_to_edit["entryDate"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    db_data = DatabaseHandler.db_entry_update(entry_to_edit, db_data, media_type, old_status, new_status)
    DatabaseHandler.db_write(db_data, db_path)

if __name__ == "__main__":
    questions = {
        "type": "list",
        "name": "entry",
        "message": "What do you want?",
        "choices": ["Add a new entry", "Edit an existing entry", "Quit"],
    }

    action = prompt(questions)

    if action.get("entry") == 'Add a new entry':
        add_entry()
    elif action.get("entry") == 'Edit an existing entry':
        edit_entry()
    elif action.get("entry") == 'Quit':
        pass