# =========================================================================== #
#                                                                             #
#  Cisco ZTP server                                  ||         ||            #
#                                                    ||         ||            #
#  Script: run.py                                   ||||       ||||           #
#                                               ..:||||||:...:||||||:..       #
#  Author: Oren Brigg                          ------------------------       #
#                                              C i s c o  S y s t e m s       #
#  Version: 0.1 beta                                                          #
#                                                                             #
# =========================================================================== #

import json
from flask import Flask
from flask import request, jsonify, make_response


app = Flask(__name__)
""" Settings """
PORT = "5000"
HOST = "0.0.0.0"

@app.route("/")
def hello():
    return "Cisco ZTP provisioning - by obrigg@cisco.com"

@app.route('/ztp.py', methods=["GET"])
def ztp_file():
    print(request.headers)
    return app.send_static_file('ztp.py')

if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
