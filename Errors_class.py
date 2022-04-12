class SearchTownError(Exception):
    def __init__(self, data):
        self.data = data
    def __str__(self):
        return self.data


class SearchHostelError(Exception):
    def __init__(self, data):
        self.data = data
    def __str__(self):
        return self.data
