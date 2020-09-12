# SPDX-License-Identifier: GPL-2.0-or-later

from functools import lru_cache

class Controller:

    def __init__(self, vsp):
        self._vsp = vsp
        self._channels = None

    def getChannels(self):
        if self._channels == None:
            data = self._vsp.queryChannels()
            self._channels = data['channelDetails']

        return self._channels

    @lru_cache(maxsize=10)
    def playChannel(self, id, businessType):
        channel = next(filter(lambda x: x['ID'] == id, self.getChannels()))

        return self._vsp.playChannel(id, channel['physicalChannels'][0]['ID'], businessType)

    def getVSP(self):
        return self._vsp
