#!/usr/bin/env python

class RingBuffer(object):
    def __init__(self, size):
        self._max = size
        self._data = []
        self.dropped_item = None
    
    def append(self, val):
        self._data.append(val)
        if len(self._data) == self._max:
            self._cur = 0
            self.append = self.__append_full
            self.get = self.__get_full
    
    def get(self):
        return self._data

    def __append_full(self, val):
        self.dropped_item = self._data[self._cur]
        self._data[self._cur] = val
        self._cur = (self._cur+1)%self._max
    
    def __get_full(self):
        return self._data[self._cur:] + self._data[:self._cur]