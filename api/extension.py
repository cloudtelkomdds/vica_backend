from flask import Blueprint, request
from database import Database
from vm_manager import VmManager
from api.api_meta.category import Category
from api.api_meta.route import Route
from api.authentication import authenticate_api_call
from model.response import Response
from message import Message
from response_status import ResponseStatus
from model.extension import Extension

api_extension = Blueprint(Category.EXTENSION, __name__)

@api_extension.route(Route.GET_ALL_EXTENSIONS, methods=["POST"])
@authenticate_api_call
def get_all_extensions(user):
    id_pbx = request.form["id_pbx"]

    if not user.is_admin:
        query = "SELECT * FROM tb_pbx WHERE id_pbx = %s AND id_user = %s"
        param = [id_pbx, user.id_user]
        db_response = Database.execute(operation=Database.READ,
                                       query=query,
                                       param=param)
        if len(db_response.data) == 0:
            response = Response(data=[],
                                message=Message.PBX_DOES_NOT_EXIST,
                                status=ResponseStatus.FAILED)
            return response.get_json()

    query = "SELECT id_extension, id_pbx, username, secret FROM tb_extension WHERE id_pbx = %s"
    param = [id_pbx]
    db_response = Database.execute(operation=Database.READ, query=query, param=param)
    extensions = []
    for item in db_response.data:
        extension = Extension(id_extension=item[0],
                              id_pbx=item[1],
                              username=item[2],
                              secret=item[3])
        extensions.append(extension.get_json())

    response = Response(data=extensions,
                        message=Message.SUCCESS,
                        status=ResponseStatus.SUCCESS)
    return response.get_json()

@api_extension.route(Route.CREATE_EXTENSION, methods=["POST"])
@authenticate_api_call
def create_extension(user):
    id_pbx = request.form["id_pbx"]
    username = request.form["username"]
    secret = request.form["secret"]

    if not user.is_admin:
        query = "SELECT * FROM tb_pbx WHERE id_pbx = %s AND id_user = %s"
        param = [id_pbx, user.id_user]
        db_response = Database.execute(operation=Database.READ,
                                       query=query,
                                       param=param)
        if len(db_response.data) == 0:
            response = Response(data=[],
                                message=Message.PBX_DOES_NOT_EXIST,
                                status=ResponseStatus.FAILED)
            return response.get_json()

    query = "SELECT number_of_extension FROM tb_pbx WHERE id_pbx = %s"
    param = [id_pbx]
    db_response = Database.execute(operation=Database.READ,
                                   query=query,
                                   param=param)
    maximum_number_of_extension = db_response.data[0][0]
    query = "SELECT * FROM tb_extension WHERE id_pbx = %s"
    param = [id_pbx]
    db_response = Database.execute(operation=Database.READ,
                                   query=query,
                                   param=param)
    current_number_of_extension = len(db_response.data)
    if current_number_of_extension >= maximum_number_of_extension:
        response = Response(data=[],
                            message=Message.EXTENSION_LIMIT_HAS_BEEN_REACHED,
                            status=ResponseStatus.FAILED)
        return response.get_json()

    query = "SELECT * FROM tb_extension WHERE id_pbx = %s AND username = %s"
    param = [id_pbx, username]
    db_response = Database.execute(operation=Database.READ,
                              query=query,
                              param=param)
    if len(db_response.data) > 0:
        response = Response(data=[],
                            message=Message.EXTENSION_ALREADY_EXIST,
                            status=ResponseStatus.FAILED)
        return response.get_json()

    update_asterisk_config(id_extension=id_pbx)

    query = "INSERT INTO tb_extension(id_pbx, username, secret) VALUES (%s, %s, %s)"
    param = [id_pbx, username, secret]
    _ = Database.execute(operation=Database.WRITE,
                         query=query,
                         param=param)
    response = Response(data=[],
                        message=Message.SUCCESS,
                        status=ResponseStatus.SUCCESS)
    return response.get_json()

@api_extension.route(Route.UPDATE_EXTENSION, methods=["POST"])
@authenticate_api_call
def update_extension(user):
    id_extension = request.form["id_extension"]
    username = request.form["username"]
    secret = request.form["secret"]

    if not user.is_admin:
        query = "SELECT * FROM tb_pbx JOIN tb_extension ON tb_pbx.id_pbx = tb_extension.id_pbx WHERE id_extension = %s AND id_user = %s"
        param = [id_extension, user.id_user]
        db_response = Database.execute(operation=Database.READ,
                                       query=query,
                                       param=param)
        if len(db_response.data) == 0:
            response = Response(data=[],
                                message=Message.EXTENSION_DOES_NOT_EXIST,
                                status=ResponseStatus.FAILED)
            return response.get_json()

    query = "UPDATE tb_extension SET username = %s, secret = %s WHERE id_extension = %s"
    param = [username, secret, id_extension]
    _ = Database.execute(operation=Database.WRITE,
                         query=query,
                         param=param)
    update_asterisk_config(id_extension=id_extension)
    response = Response(data=[],
                        message=Message.SUCCESS,
                        status=ResponseStatus.SUCCESS)
    return response.get_json()

@api_extension.route(Route.DELETE_EXTENSION, methods=["POST"])
@authenticate_api_call
def delete_extension(user):
    id_extension = request.form["id_extension"]

    if not user.is_admin:
        query = "SELECT * FROM tb_pbx JOIN tb_extension ON tb_pbx.id_pbx = tb_extension.id_pbx WHERE id_extension = %s AND id_user = %s"
        param = [id_extension, user.id_user]
        db_response = Database.execute(operation=Database.READ,
                                       query=query,
                                       param=param)
        if len(db_response.data) == 0:
            response = Response(data=[],
                                message=Message.EXTENSION_DOES_NOT_EXIST,
                                status=ResponseStatus.FAILED)
            return response.get_json()
    update_asterisk_config(id_extension=id_extension)

    query = "DELETE FROM tb_extension WHERE id_extension = %s"
    param = [id_extension]
    _ = Database.execute(operation=Database.WRITE,
                         query=query,
                         param=param)
    response = Response(data=[],
                        message=Message.SUCCESS,
                        status=ResponseStatus.SUCCESS)
    return response.get_json()

def update_asterisk_config(id_pbx=None, id_extension=None):
    if id_pbx is None and id_extension is not None:
        query = "SELECT vm_address, vm_local_address, tb_pbx.id_pbx FROM tb_pbx JOIN tb_extension ON tb_pbx.id_pbx = tb_extension.id_pbx WHERE id_extension = %s"
        param = [id_extension]
        db_response = Database.execute(operation=Database.READ,
                                       query=query,
                                       param=param)
        vm_address = db_response.data[0][0]
        vm_local_address = db_response.data[0][1]
        id_pbx = db_response.data[0][2]
    else:
        query = "SELECT vm_address, vm_local_address FROM tb_pbx WHERE id_pbx = %s"
        param = [id_pbx]
        db_response = Database.execute(operation=Database.READ,
                                       query=query,
                                       param=param)
        vm_address = db_response.data[0][0]
        vm_local_address = db_response.data[0][1]

    query = "SELECT id_extension, username, secret FROM tb_extension WHERE id_pbx = %s"
    param = [id_pbx]
    db_response = Database.execute(operation=Database.READ,
                                   query=query,
                                   param=param)
    extensions = []
    for item in db_response.data:
        extension = Extension(id_extension=item[0],
                              username=item[1],
                              secret=item[2],
                              id_pbx=id_pbx)
        extensions.append(extension)

    VmManager.update_sip_config(external_address=vm_address, local_address=vm_local_address, extensions=extensions)
    VmManager.update_extensions_config(external_address=vm_address, extensions=extensions)