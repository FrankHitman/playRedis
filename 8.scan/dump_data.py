import redis

if __name__ == '__main__':
    client = redis.StrictRedis(port=6679)
    for i in range(10000):
        client.set('key%d' % i, i)
