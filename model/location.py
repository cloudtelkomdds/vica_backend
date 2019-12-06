class Location:
    KEY_ID_LOCATION = "id_location"
    KEY_NAME = "location_name"

    def __init__(self, id_location, name):
        self.id_location = id_location
        self.name = name

    def get_json(self):
        return {
            self.KEY_ID_LOCATION: self.id_location,
            self.KEY_NAME: self.name
        }