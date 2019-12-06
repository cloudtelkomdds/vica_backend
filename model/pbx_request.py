class PbxRequest:
    KEY_ID_PBX_REQUEST = "id_pbx_request"
    KEY_ID_USER = "id_user"
    KEY_NAME = "pbx_request_name"
    KEY_LOCATION = "location"
    KEY_NUMBER_OF_EXTENSION = "number_of_extension"
    KEY_STATUS = "status"

    STATUS_APPROVED = "Approved"
    STATUS_PENDING = "Pending"
    STATUS_DEFAULT = STATUS_PENDING

    def __init__(self, id_pbx_request, id_user, name, location, number_of_extension, status):
        self.id_pbx_request = id_pbx_request
        self.id_user = id_user
        self.name = name
        self.location = location
        self.number_of_extension = number_of_extension
        self.status = status

    def get_json(self):
        return {
            self.KEY_ID_PBX_REQUEST: self.id_pbx_request,
            self.KEY_ID_USER: self.id_user,
            self.KEY_NAME: self.name,
            self.KEY_LOCATION: self.location,
            self.KEY_NUMBER_OF_EXTENSION: self.number_of_extension,
            self.KEY_STATUS: self.status
        }