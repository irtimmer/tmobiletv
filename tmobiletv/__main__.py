# SPDX-License-Identifier: GPL-2.0-or-later

import api
import yaml
from vsp import VSP

from flask import Flask

def main():
    with open("config.yml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        vsp = VSP(config)
        vsp.login()
        vsp.authenticate()
        vsp.onLineHeartbeat()
        vsp.queryChannels()

        api.vsp = vsp

        app = Flask(__name__)
        app.register_blueprint(api.bp)
        app.run()

if __name__ == "__main__":
    main()
