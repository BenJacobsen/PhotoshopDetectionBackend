from exceptions import BadRequest
class Credentials():
    username = ""
    password = ""

    def __init__(self, username, password):
        if username == "":
            raise BadRequest('A username must not be null')
        if password == "":
            raise BadRequest('A password must not be null')
        self.username = username
        self.password = password