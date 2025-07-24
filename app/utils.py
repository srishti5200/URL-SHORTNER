# TODO: Implement utility functions here
# Consider functions for:
# - Generating short codes
# - Validating URLs
# - Any other helper functions you need
# app/utils.py
import random
import string
import re
import datetime # Import datetime for the ShortenedURL model's creation timestamp
from app.models import ShortenedURL # Import the ShortenedURL class from models.py

def generate_short_code(length: int = 6) -> str:
    """
    Generates a random alphanumeric short code of a specified length.

    Args:
        length (int): The desired length of the short code. Defaults to 6.

    Returns:
        str: A randomly generated alphanumeric string.
    """
    characters = string.ascii_letters + string.digits # A-Z, a-z, 0-9
    return ''.join(random.choice(characters) for _ in range(length))

def validate_url(url: str) -> bool:
    """
    Performs a basic validation of a URL.
    Checks if the URL starts with 'http://' or 'https://' and has a domain part.

    Args:
        url (str): The URL string to validate.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    # Simple regex to check for http/https protocol and a non-empty domain
    # This regex is basic and can be expanded for more rigorous validation
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
        r'localhost|' # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(url_pattern, url) is not None

class URLManager:
    """
    Manages the storage and retrieval of shortened URLs.
    This acts as a simple in-memory database for demonstration purposes.
    In a real application, this would interact with a persistent database.
    """
    def __init__(self):
        # Stores short_code -> ShortenedURL object mapping
        self._urls = {}

    def add_url(self, original_url: str) -> ShortenedURL:
        """
        Adds a new URL to the manager, generating a unique short code for it.

        Args:
            original_url (str): The original URL to shorten.

        Returns:
            ShortenedURL: The newly created ShortenedURL object.

        Raises:
            ValueError: If the original_url is invalid.
        """
        if not validate_url(original_url):
            raise ValueError("Invalid URL provided. Please ensure it starts with http:// or https://")

        # Check if the original URL has already been shortened to prevent duplicates
        for short_url_obj in self._urls.values():
            if short_url_obj.original_url == original_url:
                # If already exists, return the existing shortened URL
                return short_url_obj

        # Generate a unique short code
        short_code = generate_short_code()
        # In a real system, you'd check database for uniqueness and retry if collision
        while short_code in self._urls:
            short_code = generate_short_code()

        new_short_url = ShortenedURL(original_url=original_url, short_code=short_code)
        self._urls[short_code] = new_short_url
        return new_short_url

    def get_url_object(self, short_code: str) -> ShortenedURL | None:
        """
        Retrieves the ShortenedURL object corresponding to a given short code.

        Args:
            short_code (str): The short code to look up.

        Returns:
            ShortenedURL | None: The ShortenedURL object if found, None otherwise.
        """
        return self._urls.get(short_code)

    def get_original_url(self, short_code: str) -> str | None:
        """
        Retrieves the original URL string corresponding to a given short code.

        Args:
            short_code (str): The short code to look up.

        Returns:
            str | None: The original URL if found, None otherwise.
        """
        short_url_obj = self.get_url_object(short_code)
        return short_url_obj.original_url if short_url_obj else None

    def increment_click(self, short_code: str):
        """
        Increments the click count for a given short code.
        """
        url_obj = self.get_url_object(short_code)
        if url_obj:
            url_obj.increment_click_count()
            # In a real database, you'd save the updated object here
            # For in-memory, just modifying the object in the dictionary is enough
            # as it's a direct reference.

    def get_all_urls(self) -> list[ShortenedURL]:
        """
        Returns a list of all stored ShortenedURL objects.

        Returns:
            list[ShortenedURL]: A list of all ShortenedURL objects.
        """
        return list(self._urls.values())

    def reset(self):
        """
        Clears all stored URLs.
        """
        self._urls = {}

# Example Usage (for testing purposes, can be removed in production)
if __name__ == "__main__":
    # Test ShortenedURL model
    url1 = ShortenedURL("https://www.example.com", "abcde1")
    print(f"Model Test: {url1}")
    print(f"Model to Dict: {url1.to_dict()}")
    url1.increment_click_count()
    print(f"Model after click: {url1}")

    # Test URLManager
    manager = URLManager()

    print("\nAdding URLs:")
    try:
        short_url1 = manager.add_url("https://www.google.com")
        print(f"Shortened: {short_url1.original_url} -> {short_url1.short_code}")

        short_url2 = manager.add_url("https://www.github.com/myprofile")
        print(f"Shortened: {short_url2.original_url} -> {short_url2.short_code}")

        short_url3 = manager.add_url("https://www.google.com") # Should return existing
        print(f"Shortened (duplicate): {short_url3.original_url} -> {short_url3.short_code}")

        # Invalid URL
        # manager.add_url("invalid-url") # Uncomment to test invalid URL
    except ValueError as e:
        print(f"Error: {e}")

    print("\nRetrieving URLs:")
    original_google = manager.get_original_url(short_url1.short_code)
    print(f"Retrieved original for {short_url1.short_code}: {original_google}")

    manager.increment_click(short_url1.short_code)
    manager.increment_click(short_url1.short_code)
    print(f"Clicks for {short_url1.short_code}: {manager.get_url_object(short_url1.short_code).click_count}")


    original_github = manager.get_original_url(short_url2.short_code)
    print(f"Retrieved original for {short_url2.short_code}: {original_github}")

    non_existent = manager.get_original_url("zzzzzz")
    print(f"Retrieved original for zzzzzz: {non_existent}")

    print("\nAll Stored URLs:")
    for url_obj in manager.get_all_urls():
        print(f"  - {url_obj.original_url} ({url_obj.short_code}) - Clicks: {url_obj.click_count}")

    manager.reset()
    print("\nManager after reset:", manager.get_all_urls())
