# -*- coding: utf-8
import redis
import threading

locks = threading.local()
locks.redis = {}


def key_for(user_id):
    return "account_{}".format(user_id)


def _lock(client, key):
    result = client.set(key, 1, nx=True, ex=5)
    return result


def _unlock(client, key):
    client.delete(key)


def lock(client, user_id):
    key = key_for(user_id)
    if key in locks.redis:
        locks.redis[key] += 1
        return True
    ok = _lock(client, key)
    if not ok:
        return False
    locks.redis[key] = 1
    return True


def unlock(client, user_id):
    key = key_for(user_id)
    if key in locks.redis:
        locks.redis[key] -= 1
        if locks.redis[key] <= 0:
            del locks.redis[key]
            _unlock(client, key)
        return True
    return False


client = redis.StrictRedis(password='739e9ec7-efd7-4e21-b68b-c4a3807b448b', host='localhost', port=6379)
print("lock", lock(client, "codehole"))
print("lock", lock(client, "codehole"))
print("unlock", unlock(client, "codehole"))
print("unlock", unlock(client, "codehole"))
