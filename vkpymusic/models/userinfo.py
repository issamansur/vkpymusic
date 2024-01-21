"""
This module contains the UserInfo class.
"""


class UserInfo:
    """
    A class that represents a user.

    Attributes:
        userid (int): The ID of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        photo (str): The URL of the user's photo.
        phone (str): The phone number of the user.
    """

    userid: int
    first_name: str
    last_name: str
    photo: str
    phone: str

    def __init__(
        self,
        userid: int,
        first_name: str,
        last_name: str,
        photo: str = "",
        phone: str = "",
    ) -> None:
        """
        Initializes a UserInfo object.

        Args:
        userid (int): The ID of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        photo (str): The URL of the user's photo.
        phone (str): The phone number of the user.
        """
        self.userid = userid
        self.first_name = first_name
        self.last_name = last_name
        self.photo = photo
        self.phone = phone

    def __str__(self):
        return f"{self.userid} {self.first_name} {self.last_name}"

    def to_dict(self) -> dict:
        """
        Converts the user to a dictionary.
        """
        return self.__dict__

    @classmethod
    def from_json(cls, item) -> "UserInfo":
        """
        Converts a JSON object to a UserInfo object.
        """
        userid = int(item["id"])
        first_name = str(item["first_name"])
        last_name = str(item["last_name"])
        if "photo_200" in item:
            photo = str(item["photo_200"])
        if "phone" in item:
            phone = str(item["phone"])
        return cls(userid, first_name, last_name, photo, phone)
