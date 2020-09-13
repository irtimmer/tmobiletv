# SPDX-License-Identifier: GPL-2.0+

import requests
import pytz
import xml.etree.ElementTree as ET

from flask import Blueprint, request, jsonify, redirect, Response
from datetime import datetime, date, time, timedelta

controller = None
bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/channel')
def channel():
    id = request.args.get('id')
    playbillID = request.args.get('playbill', None)
    businessType = request.args.get('businessType', 'BTV' if playbillID is None else 'CUTV')
    resp = controller.playChannel(id, businessType, playbillID)

    format = request.args.get('format', 'json')
    if format == 'json':
        return jsonify(resp)
    elif format == 'mpd':
        return redirect(resp['playURL'])

@bp.route('/channels')
def channels():
    radio = request.args.get('radio', False) == '1'
    channels = controller.getChannels(radio)
    props = controller.getChannelProps()

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
            options = [
                'tvg-id="%s"' % (channel['ID']),
                'tvg-name="%s"' % (channel['code']),
            ]
            if 'picture' in channel:
                options.append('tvg-logo="%s"' % (channel['picture']['icons'][0]))

            channelProps = props[channel['ID']]['physicalChannelsDynamicProperties'][0]
            if 'cutvCR' in channelProps and channelProps['cutvCR']['isValid'] == '1':
                catchup = "%sapi/channel?id=%s&format=mpd&playbill={catchup-id}" % (request.url_root, channel['ID'])
                options.append('catchup="vod"')
                options.append('catchup-days="7"')
                options.append('catchup-source="%s"' % (catchup))

            lines.append('#EXTINF:-1 %s,%s' % (' '.join(options), channel['name']))
            lines.append('#KODIPROP:inputstreamaddon=inputstream.adaptive')
            lines.append('#KODIPROP:inputstream.adaptive.manifest_type=mpd')
            if channel['physicalChannels'][0]['channelEncrypt']['encrypt'] == '1':
                lines.append('#KODIPROP:inputstream.adaptive.license_type=com.widevine.alpha')
                lines.append('#KODIPROP:inputstream.adaptive.license_key=%sapi/license?id=%s||R{SSM}|' % (request.url_root, channel['ID']))

            lines.append('%sapi/channel?id=%s&format=mpd' % (request.url_root, channel['ID']))

        return '\n'.join(lines)   

@bp.route('/epg')
def epg():
    radio = request.args.get('radio', False) == '1'
    channels = controller.getChannels(radio)
    tz = pytz.timezone(controller.getVSP()._timeZone)
    today = tz.localize(datetime.combine(date.today(), time()))
    daysBefore = int(request.args.get('daysBefore', 3))
    daysAfter = int(request.args.get('daysAfter', 3))
    startTime = today - timedelta(days=daysBefore)
    endTime = today + timedelta(days=daysAfter)
    resp = controller.getEPG(list(map(lambda x: x['ID'], channels)), startTime, endTime)

    format = request.args.get('format', 'json')
    if format == 'json':
        return jsonify(resp)
    elif format == 'xmltv':
        root = ET.Element('tv')
        for channel, playbills in zip(channels, resp):
            xch = ET.SubElement(root, 'channel', attrib={
                'id': channel['ID']
            })
            ET.SubElement(xch, 'display-name').text = channel['name']

            for playbill in playbills['playbillLites']:
                startTime = datetime.fromtimestamp(int(playbill['startTime']) / 1000, tz)
                stopTime = datetime.fromtimestamp(int(playbill['endTime']) / 1000, tz)
                attribs = {
                    'channel': channel['ID'],
                    'start': startTime.strftime('%Y%m%d%H%M%S %z'),
                    'stop': stopTime.strftime('%Y%m%d%H%M%S %z')
                }
                if playbill['isCUTV'] == '1':
                    attribs['catchup-id'] = playbill['ID']

                xprog = ET.SubElement(root, 'programme', attrib=attribs)
                ET.SubElement(xprog, 'title').text = playbill['name']

        return Response(ET.tostring(root, encoding='utf8', method='xml'), mimetype='text/xml')

@bp.route('/license', methods=['POST'])
def license():
    id = request.args.get('id')
    businessType = request.args.get('businessType', 'BTV')
    resp = controller.playChannel(id, businessType)

    url = resp['authorizeResult']['triggers'][0]['licenseURL']
    customData = resp['authorizeResult']['triggers'][0]['customData']
    vsp = controller.getVSP()
    resp = vsp.getSession().request(request.method, url, allow_redirects=False, data=request.get_data(), headers={
        "X_CSRFToken": vsp._auth._csrfToken,
        "CADeviceType": "Widevine OTT client",
        "AcquireLicense.CustomData": customData,
    })

    return Response(resp.content)
