from flask import Blueprint

from database import Database
from api.api_meta.category import Category
from api.api_meta.route import Route
from api.authentication import authenticate_api_call
from model.response import Response
from model.location import Location
from message import Message
from response_status import ResponseStatus

api_miscellaneous = Blueprint(Category.MISCELLANEOUS, __name__)

@api_miscellaneous.route(Route.GET_LOCATIONS, methods=["GET"])
@authenticate_api_call
def get_locations(_):
    query = "SELECT id_location, name FROM tb_location"
    db_response = Database.execute(operation=Database.READ,
                                   query=query)
    locations = []
    for item in db_response.data:
        location = Location(id_location=item[0],
                            name=item[1])
        locations.append(location.get_json())

    response = Response(data=locations,
                        message=Message.SUCCESS,
                        status=ResponseStatus.SUCCESS)
    return response.get_json()