import requests
import json
import logging

# Initialize logger
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

class AtombergCloudAPI:
    """Atomberg Cloud API to fetch all devices and save to JSON."""

    def __init__(self, api_key: str, refresh_token: str) -> None:
        self._base_url = "https://api.developer.atomberg-iot.com"
        self._api_key = api_key
        self._refresh_token = refresh_token
        self._access_token = None

    def get_access_token(self):
        """Fetch an access token using the refresh token."""
        url = f"{self._base_url}/v1/get_access_token"
        headers = {"Authorization": f"Bearer {self._refresh_token}"}
        response = requests.get(url, headers=headers)

        # Log the response for debugging
        _LOGGER.debug("Access token response: %s", response.text)

        if response.ok:
            data = response.json()
            if data.get("status") == "Success":
                self._access_token = data["message"]["access_token"]
                _LOGGER.info("Access token retrieved successfully.")
                return
        _LOGGER.error("Failed to retrieve access token: %s", response.text)

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
        response = requests.get(url, headers=headers)

        _LOGGER.debug("Devices response: %s", response.text)

        if response.ok:
            devices_data = response.json()
            if devices_data.get("status") == "Success":
                return devices_data["message"]["devices_list"]
            else:
                _LOGGER.error(
                    "Failed to fetch devices: %s", devices_data.get("message")
                )
        else:
            _LOGGER.error("HTTP error while fetching devices: %s", response.text)
        return []

    def save_devices_to_json(self, filename: str):
        """Save the fetched devices data to a JSON file."""
        devices = self.get_devices()
        if devices:
            with open(filename, "w", encoding="utf-8") as json_file:
                json.dump(devices, json_file, indent=4)
            _LOGGER.info("Devices saved to %s successfully.", filename)
        else:
            _LOGGER.error("No devices to save.")

# Replace these with your actual API credentials
API_KEY = "QEBUa2kHlz2bH2davQTO52O6AZNZBaA88lHxtyrS"  # Your API key
REFRESH_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImI5YTM3YTU1LTZiYWUtNGNiZi1hNWYzLTc1Yzc3MWI2ZDdkZSIsInR5cGUiOiJyZWZyZXNoIiwiaXNzIjoiZGV2ZWxvcGVyLmF0b21iZXJnLWlvdC5jb20iLCJkZXZlbG9wZXJfaWQiOiI3OTNleWE0czVlIiwianRpIjoiMWQyYmRiOWEtZTNmZC00NTRlLTk0MjMtZGViYTJjNDMzNDYyIiwiaWF0IjoxNzMzMDMxNzYxLCJleHAiOjIwNDgzOTE3NjF9.WklYEDPANEehqsZHnwc0nHWCps3K7GN2SJAedwUb7Oc"  # Your refresh token

if __name__ == "__main__":
    atomberg_api = AtombergCloudAPI(API_KEY, REFRESH_TOKEN)
    atomberg_api.save_devices_to_json("hi.json")
