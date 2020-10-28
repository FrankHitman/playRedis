# -*- coding: utf-8 -*-
import time
import redis

if __name__ == '__main__':
    client = redis.StrictRedis()
    p = client.pubsub()
    p.subscribe("codehole")
    for msg in p.listen():
        print(msg)
