class Profile:

    def __init__(self, person_id=None, username=None, bio=None, picture=None):
        self._person_id = person_id
        self._username = username
        self._bio = bio
        self._picture = picture

    @property
    def person_id(self):
        return self._person_id

    @property
    def username(self):
        return self._username

    @property
    def bio(self):
        return self._bio

    @property
    def picture(self):
        return self._picture

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
