import requests

# API configuration
API_URL = "https://api.api-ninjas.com/v1/animals?name="
API_KEY = "YOUR_API_KEY"  # Replace with your actual API key
HEADERS = {'X-Api-Key': API_KEY}


def fetch_animal_data(animal_name):
    """Fetch all matching animal data from API Ninja's Animals API."""
    response = requests.get(API_URL + animal_name, headers=HEADERS, timeout=10)

    if response.status_code == 200:
        data = response.json()
        if data:  # Ensure response contains data
            return data  # Return all matching animals
    return []