# SPDX-License-Identifier: GPL-2.0+

from flask import Blueprint, request, jsonify

vsp = None
bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/channel')
def channel():
    code = request.args.get('code')
    resp = vsp.playChannel(code)

    return jsonify(resp)
