# coding: utf-8

# code 1
# import redis
#
# client = redis.StrictRedis(host='127.0.0.1', port=6479)
# for i in range(1000):
#     client.pfadd("codehole", "user%d" % i)
#     total = client.pfcount("codehole")
#     if total != i + 1:
#         print(total, i + 1)
#         break

# code 2
import redis

client = redis.StrictRedis(host='127.0.0.1', port=6479)
for i in range(100000):
    client.pfadd("codehole", "user%d" % i)
print(100000, client.pfcount('codehole'))
