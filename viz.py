#!/usr/bin/env python

from pyprocessing import *
import redis
import multiprocessing
import Queue

from ringbuffer import RingBuffer
from color import ColorFader
from text import SmoothText

ring = None
queue = None
last_time = None
last_len = 0
state = 0
animation_start_time = 0
last_dropped = None
scroller = None

NEW_MESSAGE_TIME = float(1000)
FADE_TIME = float(5)
FADE_WAIT = float(2)
RETWEET_START_COLOR = color(128,128,180)
RETWEET_END_COLOR = color(90)
ORIG_START_COLOR = color(255)
ORIG_END_COLOR = color(90)

class MessageItem(object):
    def __init__(self, str):
        (self.is_retweeted, self.text) = str.split("|",1)
        self.is_retweeted = self.is_retweeted == "True"
        self.timestamp = 0
        if (not self.is_retweeted):
            self.color_fader = ColorFader(ORIG_START_COLOR, ORIG_END_COLOR, FADE_WAIT*1.5, FADE_TIME)
        else:
            self.color_fader = ColorFader(RETWEET_START_COLOR, RETWEET_END_COLOR, FADE_WAIT, FADE_TIME)
    
    @property
    def color(self):
        self.color_fader.update(millis())
        return self.color_fader.color

def add_messages_to_queue(queue):
    server = redis.StrictRedis()
    sub = server.pubsub()
    sub.subscribe("twit")
    while True:
        for message in sub.listen():
            msg = MessageItem(message['data'])
            queue.put(MessageItem(message['data']))

def setup():
    global scroller
    global queue
    
    # size(fullscreen=True)
    size(screen.width-150, 500)
    rectMode(CENTER)
    frameRate(20)
    loop()
    textSize(16)
    
    scroller = SmoothText(queue, height, 1000, 1500)

def draw():
    global scroller
    
    scroller.draw(millis())

if __name__ == '__main__':
    queue = multiprocessing.Queue()
    
    message_pump = multiprocessing.Process(target=add_messages_to_queue, args=(queue,))
    message_pump.start()
    
    run()