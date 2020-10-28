# coding:utf-8
import redis
import time

client = redis.StrictRedis(port=6479, charset="utf-8", decode_responses=True)


# 指定用户 user_id 的某个行为 action_key 在特定的时间内 period 只允许发生一定的次数 max_count
def is_action_allowed(user_id, action_key, period, max_count):
    key = user_id + action_key
    result = client.exists(key)
    if result:
        count = client.get(key)
        # count = int.from_bytes(count, 'big')
        count = int(count)
        if count > 0:
            client.incrby(key, -1)
            return True
    else:
        client.setex(key, period, max_count - 1)
        return True
    return False


# 调用这个接口 , 一分钟内只允许最多回复 5 个帖子
# can_reply = is_action_allowed("laoqian", "reply", 60, 5)
# if can_reply:
#     do_reply()
# else:
#     raise ActionThresholdOverflow()

for i in range(60):
    print(is_action_allowed("laoqian", "reply", 20, 5))
    time.sleep(1)

# output
# True
# True
# True
# True
# True
# False
# False
# False
# False
# False
# False
# False
# False
# False
# False
# False
# False
# False
# False
# False
# True
# True
# True
# True
# True
# False
# False
# False
# False
# False
# False
# False
# False
# False
# False
# False
# False
# False
# False
# False
# True
# True
# True
# True
# True
# False
# False
# False
# False
# False
# False
# False
# False
# False
# False
# False
# False
# False
# False
# False


# int.from_bytes(b'\x00\x10','big')
# 16 = 0x0010 = 0*16^1+1*16^1
# int.from_bytes(b'\x00\x10','little')
# 4096 = 0x1000 = 1*16^3
# int.from_bytes(b'\x00\x01','little')
# 256 = 0x0100 = 1*16^2
# int.from_bytes(b'\x00\x01','big')
# 1 = 0x0001 = 1*16^0
