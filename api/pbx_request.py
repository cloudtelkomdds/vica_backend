from flask import Blueprint, request

from database import Database
from vm_manager import VmManager
from api.api_meta.category import Category
from api.api_meta.route import Route
from api.authentication import authenticate_api_call
from model.response import Response
from message import Message
from response_status import ResponseStatus
from model.pbx_request import PbxRequest
from model.email import Email
from email_manager import EmailManager
from calendar_manager import CalendarManager

api_pbx_request = Blueprint(Category.PBX_REQUEST, __name__)
vm_manager = VmManager()

@api_pbx_request.route(Route.CREATE_PBX_REQUEST, methods=["POST"])
@authenticate_api_call
def create_pbx_request(user):
    name = request.form["name"]
    location = request.form["location"]
    number_of_extension = request.form["number_of_extension"]

    query = "SELECT name FROM tb_pbx_request WHERE id_user = %s"
    param = [user.id_user]
    db_response = Database.execute(operation=Database.READ,
                                   query=query,
                                   param=param)
    for item in db_response.data:
        if name == item[0]:
            response = Response(data=[],
                                message=Message.PBX_REQUEST_ALREADY_EXIST,
                                status=ResponseStatus.SUCCESS)
            return response.get_json()

    date = CalendarManager.get_now_date()
    query = "INSERT INTO tb_pbx_request(id_user, name, location, number_of_extension, status, date) VALUES (%s, %s, %s, %s, %s, %s)"
    param = [user.id_user, name, location, number_of_extension, PbxRequest.STATUS_DEFAULT, date]
    _ = Database.execute(operation=Database.WRITE,
                         query=query,
                         param=param)

    email_subject = "New PBX Request"
    email_body = "Hello Admin. There is a new PBX Request {0}. Please take a look in the web admin.".format(name)
    destination = "cloudtelkomdds@gmail.com"
    an_email = Email(subject=email_subject,
                     body=email_body,
                     destination=destination)
    EmailManager.send_email(an_email)

    response = Response(data=[],
                        message=Message.SUCCESS,
                        status=ResponseStatus.SUCCESS)
    return response.get_json()

@api_pbx_request.route(Route.GET_ALL_PBX_REQUESTS, methods=["GET"])
@authenticate_api_call
def get_all_pbx_requests(user):
    pbx_requests = []
    if not user.is_admin:
        query = "SELECT id_pbx_request, name, location, number_of_extension, status, date FROM tb_pbx_request WHERE id_user = %s"
        param = [user.id_user]
        db_response = Database.execute(operation=Database.READ,
                                       query=query,
                                       param=param)
        for item in db_response.data:
            pbx_request = PbxRequest(id_pbx_request=item[0],
                                     name=item[1],
                                     location=item[2],
                                     number_of_extension=item[3],
                                     status=item[4],
                                     id_user= user.id_user,
                                     date=item[5])
            if pbx_request.status != PbxRequest.STATUS_APPROVED:
                pbx_requests.append(pbx_request.get_json())
    else:
        query = "SELECT tb_user.id_user, tb_user.name, id_pbx_request, tb_pbx_request.name, location, number_of_extension, status, date, tb_user.email FROM tb_user JOIN tb_pbx_request ON tb_user.id_user = tb_pbx_request.id_user"
        db_response = Database.execute(operation=Database.READ,
                                       query=query)
        for item in db_response.data:
            pbx_request = PbxRequest(id_pbx_request=item[2],
                                     name=item[3],
                                     location=item[4],
                                     number_of_extension=item[5],
                                     status=item[6],
                                     id_user=item[0],
                                     date=item[7])
            pbx_request_json = pbx_request.get_json()
            pbx_request_json["user_name"] = item[1]
            pbx_request_json["user_email"] = item[8]
            if pbx_request.status != PbxRequest.STATUS_APPROVED:
                pbx_requests.append(pbx_request_json)

    response = Response(data=pbx_requests,
                        message=Message.SUCCESS,
                        status=ResponseStatus.SUCCESS)
    return response.get_json()

@api_pbx_request.route(Route.APPROVE_PBX_REQUEST, methods=["POST"])
@authenticate_api_call
def approve_pbx_request(user):
    if not user.is_admin:
        response = Response(data=[],
                            message=Message.AUTHENTICATION_FAILED,
                            status=ResponseStatus.FAILED)
        return response.get_json()

    id_pbx_request = request.form["id_pbx_request"]

    query = "SELECT id_user, name, location, number_of_extension, status FROM tb_pbx_request WHERE id_pbx_request = %s"
    param = [id_pbx_request]
    db_response = Database.execute(operation=Database.READ,
                                   query=query,
                                   param=param)
    status = db_response.data[0][4]
    if status == PbxRequest.STATUS_APPROVED:
        response = Response(data=[],
                            message=Message.PBX_REQUEST_ALREADY_APPROVED,
                            status=ResponseStatus.FAILED)
        return response.get_json()

    id_user = db_response.data[0][0]
    name = db_response.data[0][1]
    vm = vm_manager.get_valid_name(id_user, name)
    location = db_response.data[0][2]
    number_of_extension = db_response.data[0][3]

    query = "SELECT email FROM tb_user WHERE id_user = %s"
    param = [id_user]
    db_response = Database.execute(operation=Database.READ,
                                   query=query,
                                   param=param)
    email = db_response.data[0][0]
    vm_manager.run(name=vm,
                   origin_pbx=name,
                   origin_email=email)

    query = "INSERT INTO tb_pbx(id_user, name, location, number_of_extension, vm_name, vm_address, vm_local_address) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    param = [id_user, name, location, number_of_extension, vm, VmManager.DEFAULT_ADDRESS, VmManager.DEFAULT_ADDRESS]
    _ = Database.execute(operation=Database.WRITE,
                         query=query,
                         param=param)
    query = "UPDATE tb_pbx_request SET status = %s WHERE id_pbx_request = %s"
    param = [PbxRequest.STATUS_APPROVED, id_pbx_request]
    _ = Database.execute(operation=Database.WRITE,
                         query=query,
                         param=param)

    response = Response(data=[],
                        message=Message.SUCCESS,
                        status=ResponseStatus.SUCCESS)
    return response.get_json()

@api_pbx_request.route(Route.DELETE_PBX_REQUEST, methods=["POST"])
@authenticate_api_call
def delete_pbx_request(user):
    id_pbx_request = request.form["id_pbx_request"]

    if not user.is_admin:
        query = "SELECT * FROM tb_pbx_request WHERE id_pbx_request = %s AND id_user = %s"
        param = [id_pbx_request, user.id_user]
        db_response = Database.execute(operation=Database.READ,
                                       query=query,
                                       param=param)
        if len(db_response.data) == 0:
            response = Response(data=[],
                                message=Message.PBX_REQUEST_DOES_NOT_EXIST,
                                status=ResponseStatus.FAILED)
            return response.get_json()
        query = "DELETE FROM tb_pbx_request WHERE id_pbx_request = %s AND id_user = %s"
        param = [id_pbx_request, user.id_user]
    else:
        query = "DELETE FROM tb_pbx_request WHERE id_pbx_request = %s"
        param = [id_pbx_request]

    _ = Database.execute(operation=Database.WRITE,
                         query=query,
                         param=param)

    response = Response(data=[],
                        message=Message.SUCCESS,
                        status=ResponseStatus.SUCCESS)
    return response.get_json()