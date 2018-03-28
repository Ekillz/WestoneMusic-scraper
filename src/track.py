import json

class Track():

    def __init__(self, title, no, album_reference, original_publisher, composers, filename):
        self.title = title
        self.no = no
        self.album_reference = album_reference
        self.original_publisher = original_publisher
        self.composers = composers
        self.filename = filename


    def toJSON(self):
        return json.dumps(self.__dict__)
