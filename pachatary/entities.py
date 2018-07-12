class Picture:

    def __init__(self, large_url=None, medium_url=None, small_url=None, tiny_url=None):
        self._large_url = large_url
        self._medium_url = medium_url
        self._small_url = small_url
        self._tiny_url = tiny_url

    @property
    def large_url(self):
        return self._large_url

    @property
    def medium_url(self):
        return self._medium_url

    @property
    def small_url(self):
        return self._small_url

    @property
    def tiny_url(self):
        return self._tiny_url
