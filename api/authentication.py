from functools import wraps
from flask import Blueprint, request
from google.auth.transport import requests
from google.oauth2 import id_token
from database import Database
from secret import Secret
from api.api_meta.category import Category
from api.api_meta.route import Route
from email_manager import EmailManager
from model.response import Response
from utils import Utils
from message import Message
from response_status import ResponseStatus
from model.user import User
from model.email import Email

api_authentication = Blueprint(Category.AUTHENTICATION, __name__)

@api_authentication.route(Route.SIGN_IN_WITH_GOOGLE, methods=["POST"])
def sign_in_with_google():
    token = request.form["token"]

    info = id_token.verify_oauth2_token(token, requests.Request(), Secret.CLIENT_ID)
    name = info["given_name"]
    email = info["email"]

    query = "SELECT id_user, name, email, is_admin, token FROM tb_user WHERE email = %s"
    param = [email]
    db_response = Database.execute(operation=Database.READ,
                                   query=query,
                                   param=param)

    if len(db_response.data) == 0:
        token = Utils.generate_token()
        query = "INSERT INTO tb_user(name, email, token) VALUES (%s, %s, %s)"
        param = [name, email, token]
        _ = Database.execute(operation=Database.WRITE,
                                       query=query,
                                       param=param)

        query = "SELECT id_user, name, email, is_admin, token FROM tb_user WHERE email = %s"
        param = [email]
        db_response = Database.execute(operation=Database.READ,
                                       query=query,
                                       param=param)

        an_email = Email(subject=Message.EMAIL_NEW_USER_LOGIN_SUBJECT,
                         body=Message.EMAIL_NEW_USER_LOGIN_BODY,
                         destination=email)
        EmailManager.send_email(an_email)

    user = User(id_user=db_response.data[0][0],
                name=db_response.data[0][1],
                email=db_response.data[0][2],
                is_admin=db_response.data[0][3],
                token=db_response.data[0][4])
    response = Response(data=user.get_json(),
                        message=Message.SUCCESS,
                        status=ResponseStatus.SUCCESS)
    return response.get_json()

def authenticate_api_call(func):
    @wraps(func)
    def authenticate_with_token():
        token = request.headers.get("Authorization")
        if token is None:
            response = Response(data=[],
                                message=Message.AUTHENTICATION_FAILED,
                                status=ResponseStatus.FAILED)
            return response.get_json()
        else:
            query = "SELECT id_user, name, email, is_admin, token FROM tb_user WHERE token = %s"
            param = [token.split(" ")[1]]
            db_response = Database.execute(operation=Database.READ,
                                           query=query,
                                           param=param)
            if len(db_response.data) == 0:
                response = Response(data=[],
                                    message=Message.AUTHENTICATION_FAILED,
                                    status=ResponseStatus.FAILED)
                return response.get_json()
            else:
                user = User(id_user=db_response.data[0][0],
                            name=db_response.data[0][1],
                            email=db_response.data[0][2],
                            is_admin=db_response.data[0][3],
                            token=db_response.data[0][4])
                return func(user)
    return authenticate_with_token