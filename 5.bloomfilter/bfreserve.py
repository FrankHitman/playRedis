# coding: utf-8

import redis
import random

client = redis.StrictRedis(port=6679)

CHARS = ''.join([chr(ord('a') + i) for i in range(26)])


def random_string(n):
    chars = []
    for i in range(n):
        idx = random.randint(0, len(CHARS) - 1)
        chars.append(CHARS[idx])
    return ''.join(chars)


users = list(set([random_string(64) for i in range(100000)]))
print('total users', len(users))
users_train = users[:len(users) / 2]
users_test = users[len(users) / 2:]

falses = 0
client.delete("codehole")
# 增加了下面这一句
client.execute_command("bf.reserve", "codehole", 0.001, 50000)
for user in users_train:
    client.execute_command("bf.add", "codehole", user)
print('all trained')
for user in users_test:
    ret = client.execute_command("bf.exists", "codehole", user)
    if ret == 1:
        falses += 1

print(falses, len(users_test))
