# SPDX-License-Identifier: GPL-2.0-or-later

from functools import lru_cache

class Controller:

    def __init__(self, vsp):
        self._vsp = vsp
        self._channels = None

    def getChannels(self, radio=False):
        if self._channels == None:
            data = self._vsp.queryChannels()
            props = self._vsp.queryAllChannelDynamicProperties()
            self._channelProps = { x['ID']: x for x in props['channelDynamaicProp'] }
            self._channels = [x for x in data['channelDetails'] if self._channelProps[x['ID']]['physicalChannelsDynamicProperties'][0]['btvCR']['isValid'] == '1']

        if not radio:
            return [x for x in self._channels if x['contentType'] == 'VIDEO_CHANNEL']
        else:
            return self._channels

    @lru_cache(maxsize=10)
    def playChannel(self, id, businessType, playbillID=None):
        channel = next(filter(lambda x: x['ID'] == id, self.getChannels()))

        return self._vsp.playChannel(id, channel['physicalChannels'][0]['ID'], businessType, playbillID)

    def getVSP(self):
        return self._vsp
