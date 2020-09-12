# SPDX-License-Identifier: GPL-2.0-or-later

import api
import yaml
from vsp import VSP
from controller import Controller

from flask import Flask
from flask_cors import CORS

def main():
    with open("config.yml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        vsp = VSP(config)
        vsp.login()
        vsp.authenticate()
        vsp.onLineHeartbeat()
        vsp.queryChannels()

        api.controller = Controller(vsp)

        app = Flask(__name__)
        CORS(app)
        app.register_blueprint(api.bp)
        app.run()

if __name__ == "__main__":
    main()
