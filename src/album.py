import json

class Album():

    def __init__(self, title, description, composers, label_name, label_code, cat_no):
        self.title = title
        self.description = description
        self.composers = composers
        self.name = label_name
        self.label_code = label_code
        self.cat_no = cat_no
        self.tracks = []


    def toJSON(self):
        return json.dumps(self.__dict__)
