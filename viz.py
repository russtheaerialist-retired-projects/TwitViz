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

NEW_MESSAGE_TIME = 1000

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

def add_messages_to_queue(queue):
    server = redis.StrictRedis()
    sub = server.pubsub()
    sub.subscribe("twit")
    while True:
        for message in sub.listen():
             queue.put(message['data'])

def setup():
    global last_time
    
    size(fullscreen=True)
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
        frameRate(2)
    else:
        frameRate(20)
    
    if state > 0:
        time = (millis() - animation_start_time) / 1000.0
        print y, y_step,
        y = lerp(y-y_step, y, time)
        print time, y
        if time > 1:
            state = 0
    
    for item in items:
        try:
            text(item, x, y)
        except UnicodeDecodeError:
            text("Unsupported Language Tweeted", x, y)
        y-= y_step
    if state == 2:
        pass # draw partial?
    
    if millis() - last_time > NEW_MESSAGE_TIME:
        try:
            new_item = queue.get_nowait()
            ring.append(new_item)
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