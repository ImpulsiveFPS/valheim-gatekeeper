import json

# Function to load data from a file
def load_file(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Function to save data to a file
def save_file(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# Function to append application data to a file
def save_application(application_data, file_path):
    applications = load_file(file_path)
    if not isinstance(applications, list):  # Ensure the file stores a list
        applications = []
    applications.append(application_data)
    save_file(file_path, applications)
