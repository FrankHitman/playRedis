# -*- coding: utf-8 -*-
import redis

if __name__ == '__main__':
    client = redis.StrictRedis(port=6679)
    client.publish("codehole", "python comes")
    client.publish("codehole", "java comes")
    client.publish("codehole", "golang comes")
