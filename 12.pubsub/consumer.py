# -*- coding: utf-8 -*-
import time
import redis

if __name__ == '__main__':
    client = redis.StrictRedis(port=6679)
    p = client.pubsub()
    p.subscribe("codehole")
    while True:
        msg = p.get_message()
        if not msg:
            time.sleep(1)
            continue
        print(msg)
