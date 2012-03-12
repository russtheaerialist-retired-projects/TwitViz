#!/usr/bin/env python

from pyprocessing import lerpColor

class ColorFader(object):
    def __init__(self, start_color, end_color, fade_wait, fade_time):
        self.start_color = start_color
        self.end_color = end_color
        self.fade_wait = fade_wait
        self.fade_time = fade_time*1000.0
        self.timestamp = 0
        self.color = self.start_color
    
    def start(self, mills):
        self.timestamp = mills
    
    def update(self, mills):
        ts = (mills - self.timestamp + self.fade_wait) / self.fade_time - self.fade_wait
        if ts < 0:
            self.color = self.start_color
        elif ts > 1:
            self.color = self.end_color
        else:
            self.color = lerpColor(self.start_color, self.end_color, ts)