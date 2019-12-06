from flask import Blueprint, request
from database import Database
from vm_manager import VmManager
from api.api_meta.category import Category
from api.api_meta.route import Route
from api.authentication import authenticate_api_call
from model.response import Response
from model.pbx import Pbx
from message import Message
from response_status import ResponseStatus

api_pbx = Blueprint(Category.PBX, __name__)
vm_manager = VmManager()

@api_pbx.route(Route.GET_ALL_PBXS, methods=["GET"])
@authenticate_api_call
def get_all_pbxs(user):
    pbxs = []
    if not user.is_admin:
        query = "SELECT id_pbx, name, vm_name, location, number_of_extension, vm_address, vm_local_address FROM tb_pbx WHERE id_user = %s"
        param = [user.id_user]
        db_response = Database.execute(operation=Database.READ,
                                       query=query,
                                       param=param)
        for item in db_response.data:
            pbx = Pbx(id_pbx=item[0],
                      name=item[1],
                      vm_name=item[2],
                      location=item[3],
                      number_of_extension=item[4],
                      vm_address=item[5],
                      vm_local_address=item[6],
                      id_user=user.id_user)
            pbxs.append(pbx.get_json())
    else:
        query = "SELECT tb_user.id_user, tb_user.name, id_pbx, tb_pbx.name, vm_name, location, number_of_extension, vm_address, vm_local_address FROM tb_user JOIN tb_pbx ON (tb_user.id_user = tb_pbx.id_user)"
        db_response = Database.execute(operation=Database.READ,
                                       query=query)
        for item in db_response.data:
            pbx = Pbx(id_user=item[0],
                      id_pbx=item[2],
                      name=item[3],
                      vm_name=item[4],
                      location=item[5],
                      number_of_extension=item[6],
                      vm_address=item[7],
                      vm_local_address=item[8])
            pbx_json = pbx.get_json()
            pbx_json["user_name"] = item[1]
            pbxs.append(pbx_json)

    response = Response(data=pbxs,
                        message=Message.SUCCESS,
                        status=ResponseStatus.SUCCESS)
    return response.get_json()

@api_pbx.route(Route.DELETE_PBX, methods=["POST"])
@authenticate_api_call
def delete_pbx(user):
    id_pbx = request.form["id_pbx"]

    if not user.is_admin:
        query = "SELECT vm_name FROM tb_pbx WHERE id_pbx = %s AND id_user = %s"
        param = [id_pbx, user.id_user]
        db_response = Database.execute(operation=Database.READ,
                                       query=query,
                                       param=param)
        if len(db_response.data) == 0:
            response = Response(data=[],
                                message=Message.PBX_DOES_NOT_EXIST,
                                status=ResponseStatus.FAILED)
            return response.get_json()
    else:
        query = "SELECT vm_name FROM tb_pbx WHERE id_pbx = %s"
        param = [id_pbx]
        db_response = Database.execute(operation=Database.READ,
                                       query=query,
                                       param=param)
    vm_name = db_response.data[0][0]
    vm_manager.remove(name=vm_name)
    query = "DELETE FROM tb_pbx WHERE id_pbx = %s"
    param = [id_pbx]
    _ = Database.execute(operation=Database.WRITE,
                         query=query,
                         param=param)

    response = Response(data=[],
                        message=Message.SUCCESS,
                        status=ResponseStatus.SUCCESS)
    return response.get_json()