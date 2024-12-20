import requests
import json
import logging

# Initialize logger
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
_LOGGER = logging.getLogger(__name__)


class AtombergCloudAPI:
    """Atomberg Cloud API to fetch all devices and save to JSON."""

    def __init__(self, api_key: str, refresh_token: str) -> None:
        if not api_key or not refresh_token:
            raise ValueError("API Key and Refresh Token must not be empty.")
        
        self._base_url = "https://api.developer.atomberg-iot.com"
        self._api_key = api_key
        self._refresh_token = refresh_token
        self._access_token = None

    def get_access_token(self):
        """Fetch an access token using the refresh token."""
        url = f"{self._base_url}/v1/get_access_token"
        headers = {"Authorization": f"Bearer {self._refresh_token}"}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Log full response for debugging
            _LOGGER.debug("Access Token Response: %s", response.text)

            data = response.json()
            if data.get("status") == "Success":
                self._access_token = data["message"]["access_token"]
                _LOGGER.info("Access token retrieved successfully.")
                return
            else:
                _LOGGER.error("Access token retrieval failed: %s", data.get("message"))

        except requests.exceptions.RequestException as e:
            _LOGGER.error("Network error while fetching access token: %s", e)
        except json.JSONDecodeError:
            _LOGGER.error("Failed to parse response for access token.")

    def get_devices(self):
        """Fetch the list of devices and their states."""
        if not self._access_token:
            self.get_access_token()
            if not self._access_token:
                _LOGGER.error("Cannot fetch devices without access token.")
                return []

        url = f"{self._base_url}/v1/get_list_of_devices"
        headers = {
            "X-API-Key": self._api_key,
            "Authorization": f"Bearer {self._access_token}",
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            _LOGGER.debug("Devices Response: %s", response.text)

            devices_data = response.json()
            if devices_data.get("status") == "Success":
                _LOGGER.info("Devices fetched successfully.")
                return devices_data["message"].get("devices_list", [])
            else:
                _LOGGER.error("Failed to fetch devices: %s", devices_data.get("message"))

        except requests.exceptions.RequestException as e:
            _LOGGER.error("Network error while fetching devices: %s", e)
        except json.JSONDecodeError:
            _LOGGER.error("Failed to parse response for devices.")
        
        return []

    def save_devices_to_json(self, filename: str):
        """Save the fetched devices data to a JSON file."""
        devices = self.get_devices()
        if devices:
            try:
                with open(filename, "w", encoding="utf-8") as json_file:
                    json.dump(devices, json_file, indent=4)
                _LOGGER.info("Devices saved to '%s' successfully.", filename)
            except IOError as e:
                _LOGGER.error("Failed to write devices to file: %s", e)
        else:
            _LOGGER.error("No devices to save.")


# Replace these with your actual API credentials
API_KEY = "g6c2gReJhk2xolAMo9oEm1CPADl292Es5YSUmEvU"  # Your API key
REFRESH_TOKEN = (
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImI5YTM3YTU1LTZiYWUtNGNiZi1hNWYzLTc1Yzc3MWI2ZDdkZSIsInR5cGUiOiJyZWZyZXNoIiwiaXNzIjoiZGV2ZWxvcGVyLmF0b21iZXJnLWlvdC5jb20iLCJkZXZlbG9wZXJfaWQiOiJzcWo0eDE1aTI0IiwianRpIjoiZWFlZTk2NTgtYzc3OS00NDA3LTgwOTgtMmNkMWZkYjQ5OGZmIiwiaWF0IjoxNzM0NDQ5NTI0LCJleHAiOjIwNDk4MDk1MjR9.khTmQc7ZqofOzv7vF7pKHhL8A_Bh3zgNWuN4-2f9XKE"
)  # Your refresh token

if __name__ == "__main__":
    try:
        atomberg_api = AtombergCloudAPI(API_KEY, REFRESH_TOKEN)
        atomberg_api.save_devices_to_json("devices.json")
    except ValueError as e:
        _LOGGER.error("Configuration error: %s", e)
