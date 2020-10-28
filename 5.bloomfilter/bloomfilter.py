# coding: utf-8


# import redis
#
# client = redis.StrictRedis(port=6679)
# client.delete("codehole")
# for i in range(100000):
#     client.execute_command("bf.add", "codehole", "user%d" % i)
#     ret = client.execute_command("bf.exists", "codehole", "user%d" % i)
#     if ret == 0:
#         print(i)
#         break

import redis

client = redis.StrictRedis(port=6679)
client.delete("codehole")
for i in range(100000):
    client.execute_command("bf.add", "codehole", "user%d" % i)
    ret = client.execute_command("bf.exists", "codehole", "user%d" % (i + 1))
    if ret == 1:
        print(i)
        break

# output
# 310
# 127.0.0.1:6679> bf.exists codehole user310
# (integer) 1
# 127.0.0.1:6679> bf.exists codehole user311
# (integer) 1
# 127.0.0.1:6679> bf.exists codehole user312
# (integer) 0
