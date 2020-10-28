# -*- coding: utf-8
import redis


def key_for(user_id):
    return "account_{}".format(user_id)


def double_account(client, user_id):
    key = key_for(user_id)
    while True:
        pipe = client.pipeline(transaction=True)
        pipe.watch(key)
        value = int(pipe.get(key))
        value *= 2  # 加倍
        pipe.multi()
        pipe.set(key, value)
        try:
            pipe.execute()
            break  # 总算成功了
        except redis.WatchError:
            continue  # 事务被打断了，重试
    return int(client.get(key))  # 重新获取余额


client = redis.StrictRedis(port=6679)
user_id = "abc"
client.setnx(key_for(user_id), 5)  # setnx 做初始化
print(double_account(client, user_id))
