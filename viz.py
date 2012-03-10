#!/usr/bin/env python

from pyprocessing import *
import redis
import multiprocessing
import Queue

ring = None
queue = None
last_time = None
last_len = 0
state = 0
animation_start_time = 0
last_dropped = None

NEW_MESSAGE_TIME = float(1000)
SECONDS_FADE = float(5000)
RETWEET_START_COLOR = color(128,128,180)
RETWEET_END_COLOR = color(90)
ORIG_START_COLOR = color(255)
ORIG_END_COLOR = color(90)

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

class MessageItem(object):
    def __init__(self, str):
        (self.is_retweeted, self.text) = str.split("|",1)
        self.is_retweeted = self.is_retweeted == "True"
        self.timestamp = 0
        if (not self.is_retweeted):
            self.start_color = ORIG_START_COLOR
            self.end_color = ORIG_END_COLOR
        else:
            self.start_color = RETWEET_START_COLOR
            self.end_color = RETWEET_END_COLOR
    
    @property
    def color(self):
        ts = (millis() - self.timestamp + (SECONDS_FADE/1000.0)) / SECONDS_FADE - (SECONDS_FADE/1000.0)
        if ts < 0:
            return self.start_color
        if ts > 1:
            return self.end_color
        retval = lerpColor(self.start_color, self.end_color, ts)
        return retval

def add_messages_to_queue(queue):
    server = redis.StrictRedis()
    sub = server.pubsub()
    sub.subscribe("twit")
    while True:
        for message in sub.listen():
             queue.put(MessageItem(message['data']))

def setup():
    global last_time
    
    # size(fullscreen=True)
    size(screen.width-150, 500)
    rectMode(CENTER)
    frameRate(20)
    loop()
    textSize(16)
    
    last_time = millis()

def draw():
    global ring
    global queue
    global last_time
    global last_len
    global state
    global animation_start_time
    global last_dropped
    
    y_step = textAscent() + textDescent()
    
    if ring is None:
        ring = RingBuffer(height / y_step)
    
    if queue is None: return
    
    background(51)
    
    x = 0
    
    items = ring.get()
    y = y_step * len(items)
    
    if len(items) > last_len:
        state = 1
        animation_start_time = millis()
        
    last_len = len(items)
    
    if state == 0:
        frameRate(15)
    else:
        frameRate(30)
    
    if state > 0:
        time = (millis() - animation_start_time) / 1000.0
        y = lerp(y-y_step, y, time)
        if time > 1:
            state = 0
    
    for item in items:
        try:
            if item is None:
                item = MessageItem("True|Something bad happened")
            fill(item.color)
            text(item.text, x, y)
        except UnicodeDecodeError:
            text("Unsupported Language Tweeted", x, y)
        y-= y_step
    if state == 2:
        pass # draw partial?
    
    if state == 0 and millis() - last_time > NEW_MESSAGE_TIME:
        try:
            new_item = queue.get_nowait()
            ring.append(new_item)
            new_item.timestamp = millis()
            print new_item.color, new_item.text
            last_dropped = ring.dropped_item
            if state != 1:
                state = 2
                animation_start_time = millis()
        except Queue.Empty:
            pass

if __name__ == '__main__':
    queue = multiprocessing.Queue()
    
    message_pump = multiprocessing.Process(target=add_messages_to_queue, args=(queue,))
    message_pump.start()
    
    run()