import json
import os

MovieTOKEN = False
fodlerPath = False
error = False
current_dir = os.getcwd()
config_file = f"{current_dir}\config.json"

try:
    with open(config_file, 'r') as file:
        file_data = json.load(file)
    MovieTOKEN = file_data.get('MovieTOKEN')
    folderPath = file_data.get('folderPath', '')
except json.JSONDecodeError:
    error = {"error": "Invalid JSON in config file"}
except Exception as e:
    error = {"error": f"Unexpected error: {str(e)}"}