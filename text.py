import Queue

from pyprocessing import textAscent, textDescent, background, frameRate, lerp, text, fill
from ringbuffer import RingBuffer

class SmoothText(object):
    def __init__(self, queue, height, new_message_time, scroll_time):
        self.queue = queue
        self.y_step = textAscent() + textDescent()
        self.y = 0
        self.ring = RingBuffer(height / self.y_step)
        self.last_time = 0
        self.new_message_time = float(new_message_time)
        self.scroll_time = float(scroll_time)
        self.animation_start_time = 0
    
    def _update_start(self, millis):
        pass
    
    def _update_end(self, millis):
        pass
    
    def _wait_for_message(self, millis):
        if millis - self.last_time > self.new_message_time:
            try:
                new_item = self.queue.get_nowait()
                self.ring.append(new_item)
                new_item.color_fader.start(millis)
                new_item.timestamp = millis
                self.animation_start_time = millis
                self._update = self._animate
            except Queue.Empty:
                pass
    
    def _animate(self, millis):
        time = (millis - self.animation_start_time) / self.scroll_time
        self.y = lerp(self.y-self.y_step, self.y, time)
        if time > 1:
            self._update = self._wait_for_message
    
    _update = _wait_for_message
    def update(self, millis):
        self._update_start(millis)
        self._update(millis)
        self._update_end(millis)
    
    def append(self, message):
        self.ring.append(message)

    def draw(self, millis):
        background(51)
        items = self.ring.get()
        (x,self.y) = (0, self.y_step * len(items))
        self.update(millis)
        for item in items:
            try:
                if item is not None:
                    fill(item.color)
                    text(item.text, x, self.y)
                else:
                    text("Something bad happened", x, self.y)
            except UnicodeDecodeError:
                text("Unsupported Language Tweeted", x, self.y)
            self.y-= self.y_step