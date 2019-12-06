class User:
    KEY_ID_USER = "id_user"
    KEY_NAME = "name"
    KEY_EMAIL = "email"
    KEY_IS_ADMIN = "is_admin"
    KEY_TOKEN = "token"

    def __init__(self, id_user, name, email, is_admin, token):
        self.id_user = id_user
        self.name = name
        self.email = email
        self.is_admin = is_admin
        self.token = token

    def get_json(self):
        return {
            self.KEY_ID_USER: self.id_user,
            self.KEY_NAME: self.name,
            self.KEY_EMAIL: self.email,
            self.KEY_IS_ADMIN: self.is_admin,
            self.KEY_TOKEN: self.token
        }