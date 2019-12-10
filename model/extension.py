class Extension:
    KEY_ID_EXTENSION = "id_extension"
    KEY_ID_PBX = "id_pbx"
    KEY_USERNAME = "username"
    KEY_SECRET = "secret"
    KEY_NAME_ASSIGNEE = "name_assignee"
    KEY_EMAIL_ASSIGNEE = "email_assignee"

    def __init__(self, id_extension, id_pbx, username, secret, name_assignee, email_assignee):
        self.id_extension = id_extension
        self.id_pbx = id_pbx
        self.username = username
        self.secret = secret
        self.name_assignee = name_assignee
        self.email_assignee = email_assignee

    def get_json(self):
        return {
            self.KEY_ID_EXTENSION: self.id_extension,
            self.KEY_ID_PBX: self.id_pbx,
            self.KEY_USERNAME: self.username,
            self.KEY_SECRET: self.secret,
            self.KEY_NAME_ASSIGNEE: self.name_assignee,
            self.KEY_EMAIL_ASSIGNEE: self.email_assignee
        }

    @staticmethod
    def get_default_extension():
        return [
            Extension(id_extension=0,
                      id_pbx=0,
                      username="99999",
                      secret="99999",
                      name_assignee="",
                      email_assignee=""),
            Extension(id_extension=0,
                      id_pbx=0,
                      username="88888",
                      secret="88888",
                      name_assignee="",
                      email_assignee="")
        ]