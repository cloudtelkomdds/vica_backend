from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
from functools import wraps
from ContainerManager import ContainerManager
from google.oauth2 import id_token
from google.auth.transport import requests
from Secret import Secret
from Database import Database
from Role import Role
import random
import string

app = Flask(__name__)
CORS(app)
db = Database()
container_manager = ContainerManager()

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
            query = "SELECT id, is_admin FROM tb_user WHERE token = %s"
            param = [token.split(" ")[1]]
            result = db.execute(operation=Database.READ, query=query, param=param)
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
    result = db.execute(operation=Database.READ, query=query, param=param)
    if len(result[1]) == 0:
        token = generate_token()
        query = "INSERT INTO tb_user(name, email, token) VALUES (%s, %s, %s)"
        param = [name, email, token]
        _ = db.execute(operation=Database.WRITE, query=query, param=param)
        query = "SELECT name, email, is_admin, token FROM tb_user WHERE email = %s"
        param = [email]
        result = db.execute(operation=Database.READ, query=query, param=param)

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
    query = "SELECT id, name FROM tb_location"
    result = db.execute(operation=Database.READ, query=query)
    data = []
    for item in result[1]:
        item_json = {
            "location_id": item[0],
            "name": item[1]
        }
        data.append(item_json)
    message = "Locations successfully obtained."
    status = 1
    return generate_response(data=data, message=message, status=status);

@app.route("/create_pbx_request", methods=["POST"])
@authenticate
def create_pbx_request(id_user, role):
    name = request.form["name"]
    location = request.form["location"]
    number_of_extension = request.form["number_of_extension"]

    query = "SELECT name FROM tb_pbx_request WHERE id_user = %s"
    param = [id_user]
    result = db.execute(operation=Database.READ, query=query, param=param)
    for item in result[1]:
        if name == item[0]:
            data = []
            message = "PBX request with specified name has existed."
            status = 0
            return generate_response(data, message, status)

    query = "INSERT INTO tb_pbx_request(id_user, name, location, number_of_extension, status) VALUES (%s, %s, %s, %s, %s)"
    param = [id_user, name, location, number_of_extension, "Waiting For Approval"]
    _ = db.execute(operation=Database.WRITE, query=query, param=param)
    data = []
    message = "PBX request successfully submitted."
    status = 1
    return generate_response(data, message, status)

@app.route("/get_all_pbx_requests", methods=["GET"])
@authenticate
def get_all_pbx_requests(id_user, role):
    data = []
    if role == Role.ADMIN:
        query = "SELECT id_user, tb_user.name, tb_pbx_request.id, tb_pbx_request.name, location, number_of_extension, status FROM tb_user JOIN (tb_pbx_request) ON (tb_user.id = tb_pbx_request.id_user)"
        result = db.execute(operation=Database.READ, query=query)
        for item in result[1]:
            item_json = {
                "id_user": item[0],
                "user_name": item[1],
                "pbx_request_id": item[2],
                "pbx_request_name": item[3],
                "location": item[4],
                "number_of_extension": item[5],
                "status": item[6]
            }
            data.append(item_json)
    else:
        query = "SELECT id, name, location, number_of_extension, status FROM tb_pbx_request WHERE id_user = %s"
        param = [id_user]
        result = db.execute(operation=Database.READ, query=query, param=param)
        for item in result[1]:
            item_json = {
                "pbx_request_id": item[0],
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
    pbx_request_id = request.form["pbx_request_id"]

    query = "SELECT host_port FROM tb_pbx"
    result = db.execute(operation=Database.READ, query=query)
    host_port = container_manager.get_port(result[1])

    query = "SELECT id_user, name, location, number_of_extension FROM tb_pbx_request WHERE id = %s"
    param = [pbx_request_id]
    result = db.execute(operation=Database.READ, query=query, param=param)
    id_user = result[1][0][0]
    name = result[1][0][1]
    container = container_manager.get_valid_name(id_user, result[1][0][1])
    location = result[1][0][2]
    number_of_extension = result[1][0][3]
    host_address = container_manager.get_host_address()
    container_address = container_manager.get_container_address()
    container_manager.run(name=container, host_port=host_port)

    query = "INSERT INTO tb_pbx(id_user, name, container, location, number_of_extension, host_address, host_port, container_address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    param = [id_user, name, container, location, number_of_extension, host_address, host_port, container_address]
    _ = db.execute(operation=Database.WRITE, query=query, param=param)

    query = "UPDATE tb_pbx_request SET status = %s WHERE id = %s"
    param = ["Approved", pbx_request_id]
    _ = db.execute(operation=Database.WRITE, query=query, param=param)
    data = []
    message = "PBX request successfully approved."
    status = 1
    return generate_response(data=data, message=message, status=status)

@app.route("/delete_pbx_request", methods=["POST"])
@authenticate
def delete_pbx_request(id_user, role):
    pbx_request_id = request.form["pbx_request_id"]

    if role == Role.ADMIN:
        query = "DELETE FROM tb_pbx_request WHERE id = %s"
        param = [pbx_request_id]
    else:
        query = "SELECT id FROM tb_pbx_request WHERE id = %s AND id_user = %s"
        param = [pbx_request_id, id_user]
        result = db.execute(operation=Database.READ, query=query, param=param)
        if len(result[1]) == 0:
            data = []
            message = "You do not have that PBX request."
            status = 0
            return generate_response(data=data, message=message, status=status)
        query = "DELETE FROM tb_pbx_request WHERE id = %s AND id_user = %s"
        param = [pbx_request_id, id_user]
    _ = db.execute(operation=Database.WRITE, query=query, param=param)
    data = []
    message = "PBX request successfully deleted."
    status = 1
    return generate_response(data=data, message=message, status=status)

@app.route("/get_all_pbxs", methods=["GET"])
@authenticate
def get_all_pbxs(id_user, role):
    data = []
    if role == Role.ADMIN:
        query = "SELECT id_user, tb_user.name, tb_pbx.id, tb_pbx.name, container, location, number_of_extension, host_address, host_port, container_address FROM tb_user JOIN (tb_pbx) ON (tb_user.id = tb_pbx.id_user)"
        result = db.execute(operation=Database.READ, query=query)
        for item in result[1]:
            item_json = {
                "id_user": item[0],
                "user_name": item[1],
                "pbx_id": item[2],
                "pbx_name": item[3],
                "container": item[4],
                "location": item[5],
                "number_of_extension": item[6],
                "host_address": item[7],
                "host_port": item[8],
                "container_address": item[9],
            }
            data.append(item_json)
    else:
        query = "SELECT id, name, container, location, number_of_extension, host_address, host_port, container_address FROM tb_pbx WHERE id_user = %s"
        param = [id_user]
        result = db.execute(operation=Database.READ, query=query, param=param)
        for item in result[1]:
            item_json = {
                "pbx_id": item[0],
                "pbx_name": item[1],
                "container": item[2],
                "location": item[3],
                "number_of_extension": item[4],
                "host_address": item[5],
                "host_port": item[6],
                "container_address": item[7]
            }
            data.append(item_json)
    message = "PBXs successfully obtained."
    status = 1
    return generate_response(data=data, message=message, status=status)

@app.route("/delete_pbx", methods=["POST"])
@authenticate
def delete_pbx(id_user, role):
    pbx_id = request.form["pbx_id"]

    if role == Role.ADMIN:
        query = "SELECT container FROM tb_pbx WHERE id = %s"
        param = [pbx_id]
    else:
        query = "SELECT container FROM tb_pbx WHERE id = %s AND id_user = %s"
        param = [pbx_id, id_user]
        result = db.execute(operation=Database.READ, query=query, param=param)
        if len(result[1]) == 0:
            data = []
            message = "You do not have that PBX."
            status = 0
            return generate_response(data=data, message=message, status=status)
    result = db.execute(operation=Database.READ, query=query, param=param)
    container = result[1][0][0]
    container_manager.remove(container)

    query = "DELETE FROM tb_pbx WHERE id = %s"
    param = [pbx_id]
    _ = db.execute(operation=Database.WRITE, query=query, param=param)
    data = []
    message = "PBX successfully deleted."
    status = 1
    return generate_response(data=data, message=message, status=status)

if __name__ == "__main__":
    app.run(host="0.0.0.0")