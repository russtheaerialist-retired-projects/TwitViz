#!/usr/bin/env python

import tweepy
import yaml
import redis
import time

def load_configuration(filename):
    return yaml.load(open(filename, "r"))

class RedisBridge(tweepy.StreamListener):
    def __init__(self, prefix):
        super(RedisBridge, self).__init__()
        self._prefix = prefix
        self._redis = redis.StrictRedis()
        
    def on_status(self, status):
        is_retweeted = status.retweeted | (u"RT" in status.text) | (u"rt" in status.text)
        message = "%s|%s: %s" % (is_retweeted, status.author.screen_name, status.text.replace("\r", "").replace("\n", ""))
        print message
        self._redis.publish(self._prefix, message)
    
    def on_error(self, status_code):
        print "ERROR: " + status_code

def get_auth(conf):
    auth = tweepy.OAuthHandler(conf['consumer_key'], conf['consumer_secret'])
    auth.set_access_token(conf['access_token'], conf['access_secret'])
    
    return auth

def start_stream(conf, *tags):
    auth = get_auth(conf)
    
    stream = tweepy.Stream(auth, RedisBridge("twit"))
    stream.filter(track=tags)
    
if __name__ == '__main__':
    conf = load_configuration("../conf.yml")
    start_stream(conf, "pycon", "pycon2012", "#pycon", "#pycon2012")
    #data = map(lambda x: "Test %d" % x, xrange(1,10))
    #r = redis.StrictRedis()
    #while True:
    #    for d in data:
    #        r.publish("twit", d)
    #        time.sleep(1)
    