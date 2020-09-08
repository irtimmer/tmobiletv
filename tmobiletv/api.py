# SPDX-License-Identifier: GPL-2.0+

from flask import Blueprint, request, jsonify, redirect

vsp = None
bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/channel')
def channel():
    code = request.args.get('code')
    resp = vsp.playChannel(code)

    format = request.args.get('format', 'json')
    if format == 'json':
        return jsonify(resp)
    elif format == 'mpd':
        return redirect(resp['playURL'])

@bp.route('/channels')
def channels():
    channels = vsp.getChannels()

    format = request.args.get('format', 'json')
    if format == 'json':
        return jsonify(channels)
    elif format == 'm3u':
        lines = ['#EXTM3U']
        for channel in channels:
            lines.append('#EXTINF:-1,%s' % (channel['name']))
            lines.append('%sapi/channel?code=%s&format=mpd' % (request.url_root, channel['code']))

        return '\n'.join(lines)
