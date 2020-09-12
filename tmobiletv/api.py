# SPDX-License-Identifier: GPL-2.0+

from flask import Blueprint, request, jsonify, redirect

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
