import random
import string

class Utils:
    TOKEN_LENGTH = 20

    @staticmethod
    def generate_token():
        token = "".join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(Utils.TOKEN_LENGTH))
        return token