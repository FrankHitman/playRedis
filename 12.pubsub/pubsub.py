# -*- coding: utf-8 -*-
import time
import redis

if __name__ == '__main__':
    client = redis.StrictRedis(port=6679)
    p = client.pubsub()
    p.subscribe("codehole")
    time.sleep(1)
    print(p.get_message())
    print(p.get_message())

    client.publish("codehole", "java comes")
    time.sleep(1)
    print(p.get_message())

    client.publish("codehole", "python comes")
    time.sleep(1)
    print(p.get_message())
    print(p.get_message())

# output
# {'type': 'subscribe', 'pattern': None, 'channel': b'codehole', 'data': 1}
# None
# {'type': 'message', 'pattern': None, 'channel': b'codehole', 'data': b'java comes'}
# {'type': 'message', 'pattern': None, 'channel': b'codehole', 'data': b'python comes'}
# None
