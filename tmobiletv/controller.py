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

    def getEPG(self, channelIDs, startTime, endTime):
        chunks = [channelIDs[i:i + 30] for i in range(0, len(channelIDs), 30)]
        ret = []

        for chunk in chunks:
            ret.extend(self._getEPG(';'.join(chunk), int(startTime.timestamp()), int(endTime.timestamp()))['channelPlaybills'])

        return ret

    @lru_cache(maxsize=20)
    def _getEPG(self, channelIDs, startTime, endTime):
        return self._vsp.queryPlaybillListStcProps(channelIDs.split(';'), str(startTime * 1000), str(endTime * 1000))

    def getVSP(self):
        return self._vsp
