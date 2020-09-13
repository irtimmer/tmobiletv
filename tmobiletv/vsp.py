# SPDX-License-Identifier: GPL-2.0-or-later

import requests

from requests.auth import AuthBase

RETCODE_SUCCESSFULLY = '000000000'
RETCODE_SESSION_EXPIRED = '125023020'

class VSPAuth(AuthBase):

    def __init__(self, vsp):
        self._vsp = vsp
        self._csrfToken = None

    def login(self):
        self._vsp.login()
        data = self._vsp.authenticate()
        self._csrfToken = data['csrfToken']
        self._vsp._userFilter = None

    def handleResponse(self, response, **kwargs):
        data = response.json()

        if data['result']['retCode'] == RETCODE_SESSION_EXPIRED:
            self.login()

            # Consume the content so we can reuse the connection for the next
            # request.
            response.content
            response.raw.release_conn()

            request = response.request
            request.request.headers['X_CSRFToken'] = self._csrfToken
            request.prepare_cookies(self._vsp.getSession().cookies)

            _r = response.connection.send(request, **kwargs)
            _r.history.append(response)

        return response

    def __call__(self, request):
        if self._csrfToken == None:
            self.login()
            request.prepare_cookies(self._vsp.getSession().cookies)

        request.headers['X_CSRFToken'] = self._csrfToken
        request.register_hook('response', self.handleResponse)

        return request

class VSP:

    def __init__(self, config):
        self._root = config['rootUrl']
        self._deviceModel = config['deviceModel']
        self._deviceType = config['deviceType']
        self._deviceID = config['deviceID']
        self._username = config['username']
        self._password = config['password']
        self._timeZone = config['timezone']
        self._lang = config['lang']
        self._session = requests.Session()
        self._auth = VSPAuth(self)
        self._userFilter = None

    def login(self):
        resp = self._session.post('%s/Login?from=throughMSAAccess' % (self._root), json = {
            "deviceModel": self._deviceModel
        })

        return resp.json()

    def authenticate(self):
        resp = self._session.post('%s/Authenticate?from=throughMSAAccess' % (self._root), json = {
            "authenticateBasic": {
                "userID": self._username,
                "userType": "0",
                "needPosterTypes": ["1","2","3","4","5","6","7"],
                "timeZone": self._timeZone,
                "isSupportWebpImgFormat": "0",
                "clientPasswd": self._password,
                "lang": self._lang
            },
            "authenticateDevice": {
                "physicalDeviceID": self._deviceID,
                "terminalID": self._deviceID,
                "deviceModel": self._deviceModel,
                "CADeviceInfos": [
                    {
                        "CADeviceType": self._deviceType,
                        "CADeviceID": self._deviceID
                    }
                ]
            },
            "authenticateTolerant": {
                "areaCode": "",
                "templateName": "",
                "subnetID": "",
                "bossID": "",
                "userGroup": ""
            }
        })

        data = resp.json()
        return data

    def onLineHeartbeat(self):
        resp = self._session.post('%s/OnLineHeartbeat?from=inMSAAccess' % (self._root), json = {}, auth = self._auth)

        data = resp.json()
        self._userFilter = data['userFilter']
        return data

    def queryChannels(self):
        if self._userFilter == None:
            self.onLineHeartbeat()

        resp = self._session.post('%s/QueryAllChannel?userFilter=%s&from=inMSAAccess' % (self._root, self._userFilter), auth = self._auth, json = {
            "isReturnAllMedia": "0"
        })

        data = resp.json()
        return data

    def queryAllChannelDynamicProperties(self):
        resp = self._session.post('%s/QueryAllChannelDynamicProperties?from=inMSAAccess' % (self._root), auth = self._auth, json = {
            "isReturnAllMedia": "0"
        })

        data = resp.json()
        return data

    def playChannel(self, channelID, mediaID, businessType, playbillID):
        resp = self._session.post('%s/PlayChannel?from=inMSAAccess' % (self._root), auth = self._auth, json = {
            "channelID": channelID,
            "mediaID": mediaID,
            "playbillID": playbillID,
            "businessType": businessType,
            "isReturnProduct": "1",
            "isHTTPS": "1",
            "checkLock": {
                "checkType":"0"
            }
        })

        data = resp.json()
        return data

    def queryPlaybillListStcProps(self, channelIDs, startTime, endTime):
        resp = self._session.post('%s/QueryPlaybillListStcProps?from=throughMSAAccess' % (self._root), auth = self._auth, json = {
            "queryChannel": {
                "channelIDs": channelIDs,
                "isReturnAllMedia": "1",
            },
            "needChannel": "0",
            "queryPlaybill": {
                "startTime": startTime,
                "endTime": endTime,
                "count": "300",
                "offset": "0",
                "type": "0",
                "isFillProgram": "1"
            }
        })

        data = resp.json()
        return data

    def getSession(self):
        return self._session
