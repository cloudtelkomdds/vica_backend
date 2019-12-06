from model.response import Response

class DatabaseResponse(Response):
    def __init__(self, data, message, status):
        super().__init__(data=data,
                         message=message,
                         status=status)