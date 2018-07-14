class Profile:

    def __init__(self, person_id=None, username=None, bio='', picture=None, is_me=False):
        self._person_id = person_id
        self._username = username
        self._bio = bio
        self._picture = picture
        self._is_me = is_me

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

    @property
    def is_me(self):
        return self._is_me

    def builder(self):
        return Profile.Builder(self)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

    class Builder:

        def __init__(self, profile):
            self._person_id = profile.person_id
            self._username = profile.username
            self._bio = profile.bio
            self._picture = profile.picture
            self._is_me = profile.is_me

        def bio(self, bio):
            self._bio = bio
            return self

        def username(self, username):
            self._username = username
            return self

        def build(self):
            return Profile(person_id=self._person_id, username=self._username,
                           bio=self._bio, picture=self._picture, is_me=self._is_me)
