
import requests

from .constants import OFD_API_KEY, OFD_API_SECRET

OFD_API_BASE_URL = "https://api.ofd.com/v1"  # Replace with the actual OFD API base URL


def get_property_data(property_id):
    """Fetches property data from the OFD API.

    Args:
        property_id: The unique identifier of the property.

    Returns:
        A dictionary containing the property data.
    """
    headers = {
        "Authorization": f"Bearer {OFD_API_KEY}:{OFD_API_SECRET}",
        "Content-Type": "application/json",
    }
    response = requests.get(
        f"{OFD_API_BASE_URL}/properties/{property_id}", headers=headers
    )
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()
