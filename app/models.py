# TODO: Implement your data models here
# Consider what data structures you'll need for:
# - Storing URL mappings
# - Tracking click counts
# - Managing URL metadata
# app/models.py
# app/models.py
import datetime
import uuid

class ShortenedURL:
    """
    Represents a single shortened URL entry.
    Includes fields for tracking click counts and managing URL metadata.
    """
    def __init__(self, original_url: str, short_code: str, id: str = None, created_at: datetime.datetime = None, click_count: int = 0):
        """
        Initializes a new ShortenedURL object.

        Args:
            original_url (str): The full, original URL.
            short_code (str): The unique short code generated for the URL.
            id (str, optional): A unique identifier for the entry. Defaults to a new UUID.
            created_at (datetime.datetime, optional): The timestamp when the entry was created.
                                                    Defaults to the current UTC time.
            click_count (int, optional): The number of times the short URL has been clicked. Defaults to 0.
        """
        self.id = id if id is not None else str(uuid.uuid4())
        self.original_url = original_url
        self.short_code = short_code
        self.created_at = created_at if created_at is not None else datetime.datetime.utcnow()
        self.click_count = click_count # Added for tracking clicks

    def to_dict(self):
        """
        Converts the ShortenedURL object to a dictionary.
        Useful for serialization (e.g., saving to a database or returning as JSON).
        """
        return {
            "id": self.id,
            "original_url": self.original_url,
            "short_code": self.short_code,
            "created_at": self.created_at.isoformat(),
            "click_count": self.click_count # Included click count
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Creates a ShortenedURL object from a dictionary.
        Useful for deserialization (e.g., loading from a database).

        Args:
            data (dict): A dictionary containing the URL data.

        Returns:
            ShortenedURL: An instance of ShortenedURL.
        """
        return cls(
            id=data.get("id"),
            original_url=data.get("original_url"),
            short_code=data.get("short_code"),
            created_at=datetime.datetime.fromisoformat(data["created_at"]) if "created_at" in data else None,
            click_count=data.get("click_count", 0) # Included click count, with default for older entries
        )

    def increment_click_count(self):
        """
        Increments the click count for this shortened URL.
        """
        self.click_count += 1

    def __repr__(self):
        """
        Returns a string representation of the ShortenedURL object for debugging.
        """
        return f"ShortenedURL(original_url='{self.original_url}', short_code='{self.short_code}', clicks={self.click_count}, id='{self.id}')"
