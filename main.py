from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
from functools import wraps
from VmManager import VmManager
from google.oauth2 import id_token
from google.auth.transport import requests
from Secret import Secret
from Database import Database
from Role import Role
import random
import string
from email_manager import EmailManager

app = Flask(__name__)
CORS(app)
vm_manager = VmManager()

def generate_token():
    n = 20
    token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))
    return token

def generate_response(data, message, status):
    response = {
        "data": data,
        "message": message,
        "status": status
    }
    return jsonify(response)

def authenticate(func):
    @wraps(func)
    def authenticate_with_token():
        token = request.headers.get("Authorization")
        if token is None:
            data = []
            message = "Authentication failed."
            status = 0
            return generate_response(data=data, message=message, status=status)
        else:
            query = "SELECT id_user, is_admin FROM tb_user WHERE token = %s"
            param = [token.split(" ")[1]]
            result = Database.execute(operation=Database.READ, query=query, param=param)
            if len(result[1]) == 0:
                data = []
                message = "Authentication failed."
                status = 0
                return generate_response(data=data, message=message, status=status)
            else:
                id_user = result[1][0][0]
                is_admin = result[1][0][1]
                role = Role.ADMIN if is_admin else Role.NONADMIN
                return func(id_user, role)
    return authenticate_with_token

@app.route("/sign_in_with_google", methods=["POST"])
def sign_in_with_google():
    token = request.form["token"]

    info = id_token.verify_oauth2_token(token, requests.Request(), Secret.CLIENT_ID)
    name = info["given_name"]
    email = info["email"]

    query = "SELECT name, email, is_admin, token FROM tb_user WHERE email = %s"
    param = [email]
    result = Database.execute(operation=Database.READ, query=query, param=param)
    if len(result[1]) == 0:
        token = generate_token()
        query = "INSERT INTO tb_user(name, email, token) VALUES (%s, %s, %s)"
        param = [name, email, token]
        _ = Database.execute(operation=Database.WRITE, query=query, param=param)
        query = "SELECT name, email, is_admin, token FROM tb_user WHERE email = %s"
        param = [email]
        result = Database.execute(operation=Database.READ, query=query, param=param)

        if result[1][0][2] != 1:
            EmailManager.send_email(result[1][0][1])

    data = {
        "name": result[1][0][0],
        "email": result[1][0][1],
        "is_admin": True if result[1][0][2] == 1 else False,
        "token": result[1][0][3]
    }

    message = "Login successful"
    status = 1
    return generate_response(data=data, message=message, status=status)

@app.route("/get_locations", methods=["GET"])
@authenticate
def get_locations(id_user, role):
    query = "SELECT id_location, name FROM tb_location"
    result = Database.execute(operation=Database.READ, query=query)
    data = []
    for item in result[1]:
        item_json = {
            "id_location": item[0],
            "name": item[1]
        }
        data.append(item_json)
    message = "Locations successfully obtained."
    status = 1
    return generate_response(data=data, message=message, status=status)

@app.route("/create_pbx_request", methods=["POST"])
@authenticate
def create_pbx_request(id_user, role):
    name = request.form["name"]
    location = request.form["location"]
    number_of_extension = request.form["number_of_extension"]

    query = "SELECT name FROM tb_pbx_request WHERE id_user = %s"
    param = [id_user]
    result = Database.execute(operation=Database.READ, query=query, param=param)
    for item in result[1]:
        if name == item[0]:
            data = []
            message = "PBX request with specified name has existed."
            status = 0
            return generate_response(data=data, message=message, status=status)

    query = "INSERT INTO tb_pbx_request(id_user, name, location, number_of_extension, status) VALUES (%s, %s, %s, %s, %s)"
    param = [id_user, name, location, number_of_extension, "Waiting For Approval"]
    _ = Database.execute(operation=Database.WRITE, query=query, param=param)
    data = []
    message = "PBX request successfully submitted."
    status = 1
    return generate_response(data, message, status)

@app.route("/get_all_pbx_requests", methods=["GET"])
@authenticate
def get_all_pbx_requests(id_user, role):
    data = []
    if role == Role.ADMIN:
        query = "SELECT tb_user.id_user, tb_user.name, id_pbx_request, tb_pbx_request.name, location, number_of_extension, status FROM tb_user JOIN tb_pbx_request ON tb_user.id_user = tb_pbx_request.id_user"
        result = Database.execute(operation=Database.READ, query=query)
        for item in result[1]:
            item_json = {
                "id_user": item[0],
                "user_name": item[1],
                "id_pbx_request": item[2],
                "pbx_request_name": item[3],
                "location": item[4],
                "number_of_extension": item[5],
                "status": item[6]
            }
            data.append(item_json)
    else:
        query = "SELECT id_pbx_request, name, location, number_of_extension, status FROM tb_pbx_request WHERE id_user = %s"
        param = [id_user]
        result = Database.execute(operation=Database.READ, query=query, param=param)
        for item in result[1]:
            item_json = {
                "id_pbx_request": item[0],
                "pbx_request_name": item[1],
                "location": item[2],
                "number_of_extension": item[3],
                "status": item[4]
            }
            data.append(item_json)
    message = "PBX requests successfully obtained."
    status = 1
    return generate_response(data=data, message=message, status=status)

@app.route("/approve_pbx_request", methods=["POST"])
@authenticate
def approve_pbx_request(id_user, role):
    if role == Role.NONADMIN:
        data = []
        message = "Authentication failed."
        status = 0
        return generate_response(data=data, message=message, status=status)

    id_pbx_request = request.form["id_pbx_request"]

    query = "SELECT id_user, name, location, number_of_extension, status FROM tb_pbx_request WHERE id_pbx_request = %s"
    param = [id_pbx_request]
    result = Database.execute(operation=Database.READ, query=query, param=param)
    status = result[1][0][4]
    if status == "Approved":
        data = []
        message = "PBX Request has been approved before."
        status = 0
        return generate_response(data=data, message=message, status=status)

    id_user = result[1][0][0]
    name = result[1][0][1]
    vm = vm_manager.get_valid_name(id_user, result[1][0][1])
    location = result[1][0][2]
    number_of_extension = result[1][0][3]
    vm_manager.run(name=vm)

    query = "INSERT INTO tb_pbx(id_user, name, location, number_of_extension, vm_name, vm_address, vm_local_address) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    param = [id_user, name, location, number_of_extension, vm, "0.0.0.0", "0.0.0.0"]
    _ = Database.execute(operation=Database.WRITE, query=query, param=param)

    query = "UPDATE tb_pbx_request SET status = %s WHERE id_pbx_request = %s"
    param = ["Approved", id_pbx_request]
    _ = Database.execute(operation=Database.WRITE, query=query, param=param)

    data = []
    message = "PBX request successfully approved."
    status = 1
    return generate_response(data=data, message=message, status=status)

@app.route("/delete_pbx_request", methods=["POST"])
@authenticate
def delete_pbx_request(id_user, role):
    id_pbx_request = request.form["id_pbx_request"]

    if role == Role.ADMIN:
        query = "DELETE FROM tb_pbx_request WHERE id_pbx_request = %s"
        param = [id_pbx_request]
    else:
        query = "SELECT * FROM tb_pbx_request WHERE id_pbx_request = %s AND id_user = %s"
        param = [id_pbx_request, id_user]
        result = Database.execute(operation=Database.READ, query=query, param=param)
        if len(result[1]) == 0:
            data = []
            message = "You do not have that PBX request."
            status = 0
            return generate_response(data=data, message=message, status=status)
        query = "DELETE FROM tb_pbx_request WHERE id_pbx_request = %s AND id_user = %s"
        param = [id_pbx_request, id_user]
    _ = Database.execute(operation=Database.WRITE, query=query, param=param)
    data = []
    message = "PBX request successfully deleted."
    status = 1
    return generate_response(data=data, message=message, status=status)

@app.route("/get_all_pbxs", methods=["GET"])
@authenticate
def get_all_pbxs(id_user, role):
    data = []
    if role == Role.ADMIN:
        query = "SELECT tb_user.id_user, tb_user.name, id_pbx, tb_pbx.name, vm_name, location, number_of_extension, vm_address, vm_local_address FROM tb_user JOIN tb_pbx ON (tb_user.id_user = tb_pbx.id_user)"
        result = Database.execute(operation=Database.READ, query=query)
        for item in result[1]:
            item_json = {
                "id_user": item[0],
                "user_name": item[1],
                "id_pbx": item[2],
                "pbx_name": item[3],
                "vm_name": item[4],
                "location": item[5],
                "number_of_extension": item[6],
                "vm_address": item[7],
                "vm_local_address": item[8]
            }
            data.append(item_json)
    else:
        query = "SELECT id_pbx, name, vm_name, location, number_of_extension, vm_address, vm_local_address FROM tb_pbx WHERE id_user = %s"
        param = [id_user]
        result = Database.execute(operation=Database.READ, query=query, param=param)
        for item in result[1]:
            item_json = {
                "id_pbx": item[0],
                "pbx_name": item[1],
                "vm_name": item[2],
                "location": item[3],
                "number_of_extension": item[4],
                "vm_address": item[5],
                "vm_local_address": item[6]
            }
            data.append(item_json)
    message = "PBXs successfully obtained."
    status = 1
    return generate_response(data=data, message=message, status=status)

@app.route("/delete_pbx", methods=["POST"])
@authenticate
def delete_pbx(id_user, role):
    id_pbx = request.form["id_pbx"]

    if role == Role.ADMIN:
        query = "SELECT vm_name FROM tb_pbx WHERE id_pbx = %s"
        param = [id_pbx]
    else:
        query = "SELECT vm_name FROM tb_pbx WHERE id_pbx = %s AND id_user = %s"
        param = [id_pbx, id_user]
        result = Database.execute(operation=Database.READ, query=query, param=param)
        if len(result[1]) == 0:
            data = []
            message = "You do not have that PBX."
            status = 0
            return generate_response(data=data, message=message, status=status)
    result = Database.execute(operation=Database.READ, query=query, param=param)
    vm = result[1][0][0]
    vm_manager.remove(name=vm)

    query = "DELETE FROM tb_pbx WHERE id_pbx = %s"
    param = [id_pbx]
    _ = Database.execute(operation=Database.WRITE, query=query, param=param)
    data = []
    message = "PBX successfully deleted."
    status = 1
    return generate_response(data=data, message=message, status=status)

@app.route("/get_all_extensions", methods=["POST"])
@authenticate
def get_all_extensions(id_user, role):
    id_pbx = request.form["id_pbx"]

    if role == Role.NONADMIN:
        query = "SELECT * FROM tb_pbx WHERE id_pbx = %s AND id_user = %s"
        param = [id_pbx, id_user]
        result = Database.execute(operation=Database.READ, query=query, param=param)
        if len(result[1]) == 0:
            data = []
            message = "You do not have that PBX."
            status = 0
            return generate_response(data=data, message=message, status=status)

    data = []
    query = "SELECT id_extension, id_pbx, username, secret FROM tb_extension WHERE id_pbx = %s"
    param = [id_pbx]
    result = Database.execute(operation=Database.READ, query=query, param=param)
    for item in result[1]:
        item_json = {
            "id_extension": item[0],
            "id_pbx": item[1],
            "username": item[2],
            "secret": item[3]
        }
        data.append(item_json)
    message = "Extensions successfully obtained."
    status = 1
    return generate_response(data=data, message=message, status=status)

@app.route("/create_extension", methods=["POST"])
@authenticate
def create_extension(id_user, role):
    id_pbx = request.form["id_pbx"]
    username = request.form["username"]
    secret = request.form["secret"]

    if role == Role.NONADMIN:
        query = "SELECT * FROM tb_pbx WHERE id_pbx = %s AND id_user = %s"
        param = [id_pbx, id_user]
        result = Database.execute(operation=Database.READ, query=query, param=param)
        if len(result[1]) == 0:
            data = []
            message = "You do not have that PBX."
            status = 0
            return generate_response(data=data, message=message, status=status)

    query = "SELECT number_of_extension FROM tb_pbx WHERE id_pbx = %s"
    param = [id_pbx]
    result = Database.execute(operation=Database.READ, query=query, param=param)
    maximum_number_of_extension = result[1][0][0]

    query = "SELECT * FROM tb_extension WHERE id_pbx = %s"
    param = [id_pbx]
    result = Database.execute(operation=Database.READ, query=query, param=param)
    current_number_of_extension = len(result[1])
    if current_number_of_extension >= maximum_number_of_extension:
        data = []
        message = "You have reached extension limit."
        status = 0
        return generate_response(data=data, message=message, status=status)

    query = "SELECT * FROM tb_extension WHERE id_pbx = %s AND username = %s"
    param = [id_pbx, username]
    result = Database.execute(operation=Database.READ, query=query, param=param)
    if len(result[1]) > 0:
        data = []
        message = "Extension with specified username has already existed."
        status = 0
        return generate_response(data=data, message=message, status=status)

    query = "INSERT INTO tb_extension(id_pbx, username, secret) VALUES (%s, %s, %s)"
    param = [id_pbx, username, secret]
    _ = Database.execute(operation=Database.WRITE, query=query, param=param)
    data = []
    message = "Extension successfully created."
    status = 1
    update_asterisk_config(id_pbx=id_pbx)
    return generate_response(data=data, message=message, status=status)

@app.route("/update_extension", methods=["POST"])
@authenticate
def update_extension(id_user, role):
    id_extension = request.form["id_extension"]
    username = request.form["username"]
    secret = request.form["secret"]

    if role == Role.NONADMIN:
        query = "SELECT * FROM tb_pbx JOIN tb_extension ON tb_pbx.id_pbx = tb_extension.id_pbx WHERE id_extension = %s AND id_user = %s"
        param = [id_extension, id_user]
        result = Database.execute(operation=Database.READ, query=query, param=param)
        if len(result[1]) == 0:
            data = []
            message = "You do not have that extension."
            status = 0
            return generate_response(data=data, message=message, status=status)

    query = "UPDATE tb_extension SET username = %s, secret = %s WHERE id_extension = %s"
    param = [username, secret, id_extension]
    _ = Database.execute(operation=Database.WRITE, query=query, param=param)
    data = []
    message = "Extension successfully updated."
    status = 1
    update_asterisk_config(id_extension=id_extension)
    return generate_response(data=data, message=message, status=status)

@app.route("/delete_extension", methods=["POST"])
@authenticate
def delete_extension(id_user, role):
    id_extension = request.form["id_extension"]

    if role == Role.NONADMIN:
        query = "SELECT * FROM tb_pbx JOIN tb_extension ON tb_pbx.id_pbx = tb_extension.id_pbx WHERE id_extension = %s AND id_user = %s"
        param = [id_extension, id_user]
        result = Database.execute(operation=Database.READ, query=query, param=param)
        if len(result[1]) == 0:
            data = []
            message = "You do not have that extension."
            status = 0
            return generate_response(data=data, message=message, status=status)

    update_asterisk_config(id_extension=id_extension)

    query = "DELETE FROM tb_extension WHERE id_extension = %s"
    param = [id_extension]
    _ = Database.execute(operation=Database.WRITE, query=query, param=param)
    data = []
    message = "Extension successfully deleted."
    status = 1
    return generate_response(data=data, message=message, status=status)

def update_asterisk_config(id_pbx=None, id_extension=None):
    if id_pbx is None and id_extension is not None:
        query = "SELECT vm_address, vm_local_address, tb_pbx.id_pbx FROM tb_pbx JOIN tb_extension ON tb_pbx.id_pbx = tb_extension.id_pbx WHERE id_extension = %s"
        param = [id_extension]
        result = Database.execute(operation=Database.READ, query=query, param=param)
        vm_address = result[1][0][0]
        vm_local_address = result[1][0][1]
        id_pbx = result[1][0][2]
    else:
        query = "SELECT vm_address, vm_local_address FROM tb_pbx WHERE id_pbx = %s"
        param = [id_pbx]
        result = Database.execute(operation=Database.READ, query=query, param=param)
        vm_address = result[1][0][0]
        vm_local_address = result[1][0][1]

    query = "SELECT username, secret FROM tb_extension WHERE id_pbx = %s"
    param = [id_pbx]
    result = Database.execute(operation=Database.READ, query=query, param=param)
    extensions = []
    for item in result[1]:
        extension = {
            "username": item[0],
            "secret": item[1]
        }
        extensions.append(extension)

    VmManager.update_sip_config(external_address=vm_address, local_address=vm_local_address, extensions=extensions)
    VmManager.update_extensions_config(external_address=vm_address, extensions=extensions)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
