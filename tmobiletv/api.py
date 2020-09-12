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
    elif format == 'm3u_kodi':
        lines = ['#EXTM3U']
        for channel in channels:
            logo = channel['picture']['icons'][0] if 'picture' in channel else ''
            lines.append('#EXTINF:-1 tvg-id="%s" tvg-name="%s" tvg-logo="%s",%s' % (channel['ID'], channel['code'], logo, channel['name']))
            lines.append('#KODIPROP:inputstreamaddon=inputstream.adaptive')
            lines.append('#KODIPROP:inputstream.adaptive.manifest_type=mpd')
            if channel['physicalChannels'][0]['channelEncrypt']['encrypt'] == '1':
                lines.append('#KODIPROP:inputstream.adaptive.license_type=com.widevine.alpha')
                lines.append('#KODIPROP:inputstream.adaptive.license_key=%sapi/license?id=%s||R{SSM}|' % (request.url_root, channel['ID']))

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
