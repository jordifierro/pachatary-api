class Experience:

    def __init__(self, title, description,
                 id=None, author_id=None, author_profile=None,
                 picture=None, is_mine=False, is_saved=False,
                 saves_count=0, share_id=None):
        self._id = id
        self._title = title
        self._description = description
        self._picture = picture
        self._author_id = author_id
        self._author_profile = author_profile
        self._is_mine = is_mine
        self._is_saved = is_saved
        self._saves_count = saves_count
        self._share_id = share_id

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title

    @property
    def description(self):
        return self._description

    @property
    def picture(self):
        return self._picture

    @property
    def author_id(self):
        return self._author_id

    @property
    def author_profile(self):
        return self._author_profile

    @property
    def is_mine(self):
        return self._is_mine

    @property
    def is_saved(self):
        return self._is_saved

    @property
    def saves_count(self):
        return self._saves_count

    @property
    def share_id(self):
        return self._share_id

    def builder(self):
        return Experience.Builder(self)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    class Builder:

        def __init__(self, experience):
            self._id = experience.id
            self._title = experience.title
            self._description = experience.description
            self._picture = experience.picture
            self._author_profile = experience.author_profile
            self._author_id = experience.author_id
            self._is_mine = experience.is_mine
            self._is_saved = experience.is_saved
            self._saves_count = experience.saves_count
            self._share_id = experience.share_id

        def id(self, id):
            self._id = id
            return self

        def title(self, title):
            self._title = title
            return self

        def description(self, description):
            self._description = description
            return self

        def picture(self, picture):
            self._picture = picture
            return self

        def author_profile(self, author_profile):
            self._author_profile = author_profile
            return self

        def author_id(self, author_id):
            self._author_id = author_id
            return self

        def is_mine(self, is_mine):
            self._is_mine = is_mine
            return self

        def is_saved(self, is_saved):
            self._is_saved = is_saved
            return self

        def saves_count(self, saves_count):
            self._saves_count = saves_count
            return self

        def share_id(self, share_id):
            self._share_id = share_id
            return self

        def build(self):
            return Experience(id=self._id, title=self._title, description=self._description,
                              picture=self._picture, author_profile=self._author_profile,
                              author_id=self._author_id, is_mine=self._is_mine, is_saved=self._is_saved,
                              saves_count=self._saves_count, share_id=self._share_id)
