# SPDX-License-Identifier: GPL-2.0+

import requests

from flask import Blueprint, request, jsonify, redirect, Response

controller = None
bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/channel')
def channel():
    id = request.args.get('id')
    businessType = request.args.get('businessType', 'BTV')
    resp = controller.playChannel(id, businessType)

    format = request.args.get('format', 'json')
    if format == 'json':
        return jsonify(resp)
    elif format == 'mpd':
        return redirect(resp['playURL'])

@bp.route('/channels')
def channels():
    channels = controller.getChannels()

    format = request.args.get('format', 'json')
    if format == 'json':
        return jsonify(channels)
    elif format == 'm3u':
        lines = ['#EXTM3U']
        for channel in channels:
            lines.append('#EXTINF:-1,%s' % (channel['name']))
            lines.append('%sapi/channel?id=%s&format=mpd' % (request.url_root, channel['ID']))

        return '\n'.join(lines)

@bp.route('/license', methods=['POST'])
def license():
    id = request.args.get('id')
    businessType = request.args.get('businessType', 'BTV')
    resp = controller.playChannel(id, businessType)

    url = resp['authorizeResult']['triggers'][0]['licenseURL']
    customData = resp['authorizeResult']['triggers'][0]['customData']
    vsp = controller.getVSP()
    resp = vsp.getSession().request(request.method, url, allow_redirects=False, data=request.get_data(), headers={
        "X_CSRFToken": vsp._csrfToken,
        "CADeviceType": "Widevine OTT client",
        "AcquireLicense.CustomData": customData,
    })

    return Response(resp.content)
