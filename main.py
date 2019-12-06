from flask import Flask
from flask_cors import CORS
from api.authentication import api_authentication
from api.extension import api_extension
from api.miscellaneous import api_miscellaneous
from api.pbx import api_pbx
from api.pbx_request import api_pbx_request

app = Flask(__name__)
CORS(app)
app.register_blueprint(api_authentication)
app.register_blueprint(api_extension)
app.register_blueprint(api_miscellaneous)
app.register_blueprint(api_pbx)
app.register_blueprint(api_pbx_request)

if __name__ == "__main__":
    app.run(host="0.0.0.0")