# queue
Redis 的消息队列不是专业的消息队列，它没有非常多的高级特性，没有 ack 保证，如果对消息的可靠性有着极致的追求，那么它就不适合使用。

## 异步消息队列
lpush + rpop

rpush + lpop

## 队列空了怎么办？
如果队列空了，客户端就会陷入 pop 的死循环，不停地 pop，没有数据。这就是浪费生命的空轮询。
空轮询不但拉高了客户端的 CPU，redis 的 QPS 也会被拉高，如果这样空轮询的客户端有几十来个，Redis 的慢查询可能会显著增多。

- 使用 sleep 来解决这个问题，让线程睡一会，睡个 1s 钟就可以了。

有个小问题，那就是睡眠会导致消息的延迟增大。如果只有 1 个消费者，那么这个延迟就是 1s。
如果有多个消费者，这个延迟会有所下降，因为每个消费者的睡觉时间是岔开来的。

- 使用brpop/blpop 阻塞读

阻塞读在队列没有数据的时候，会立即进入休眠状态，一旦数据到来，则立刻醒过来。消息的延迟几乎为零。

### 空闲连接自动断开问题
如果线程一直阻塞在哪里，Redis 的客户端连接就成了闲置连接，闲置过久，服务器一般会主动断开连接，减少闲置资源占用。
这个时候blpop/brpop会抛出异常来。

所以编写客户端消费者的时候要小心，注意捕获异常，还要重试。

```golang
    args = append(args, timeout)
    value, err := execRedisCommand("BLPOP", args...)
    if err != nil {
        return "", err
    }
    if value == nil {
        return "", ErrRedisNil
    }
```

## 应用
### 锁冲突处理
上节课我们讲了分布式锁的问题，但是没有提到客户端在处理请求时加锁没加成功怎么办。一般有 3 种策略来处理加锁失败：

- 直接抛出异常，通知用户稍后重试；

这种方式比较适合由用户直接发起的请求，用户看到错误对话框后，会先阅读对话框的内容，再点击重试，这样就可以起到人工延时的效果。
如果考虑到用户体验，可以由前端的代码替代用户自己来进行延时重试控制。
- sleep 一会再重试；

sleep 会阻塞当前的消息处理线程，会导致队列的后续消息处理出现延迟。如果碰撞的比较频繁或者队列里消息比较多，sleep 可能并不合适。
如果因为个别死锁的 key 导致加锁不成功，线程会彻底堵死，导致后续消息永远得不到及时处理。
- 将请求转移至延时队列，过一会再试；

这种方式比较适合异步消息处理，将当前冲突的请求扔到另一个队列延后处理以避开冲突。

## 延时队列的实现
延时队列可以通过 Redis 的 zset(有序列表) 来实现。我们将消息序列化成一个字符串作为 zset 的value，这个消息的到期处理时间作为score，
然后用多个线程轮询 zset 获取到期的任务进行处理，多个线程是为了保障可用性，万一挂了一个线程还有其它线程可以继续处理。因为有多个线程，
所以需要考虑并发争抢任务，确保任务不能被多次执行。

```python
import uuid
import json
import time
from redis import Redis

redis = Redis()


def delay(msg):
    msg.id = str(uuid.uuid4())  # 保证 value 值唯一
    value = json.dumps(msg)
    retry_ts = time.time() + 5  # 5 秒后重试
    redis.zadd("delay-queue", retry_ts, value)


def loop():
    while True:
        # 最多取 1 条
        values = redis.zrangebyscore("delay-queue", 0, time.time(), start=0, num=1)
        if not values:
            time.sleep(1)  # 延时队列空的，休息 1s
            continue
        value = values[0]  # 拿第一条，也只有一条
        success = redis.zrem("delay-queue", value)  # 从消息队列中移除该消息
        if success:  # 因为有多进程并发的可能，最终只会有一个进程可以抢到消息
            msg = json.loads(value)
            handle_msg(msg)

```

Redis 的 zrem 方法是多线程多进程争抢任务的关键，它的返回值决定了当前实例有没有抢到任务，因为 loop 方法可能会被多个线程、多个进程调用，
同一个任务可能会被多个进程线程抢到，通过 zrem 来决定唯一的属主。

同时，我们要注意一定要对 handle_msg 进行异常捕获，避免因为个别任务处理问题导致循环异常退出。
如果执行错误还可以把任务重新放入有序列表，留待下一次重试。

上面的算法中同一个任务可能会被多个进程取到之后再使用 zrem 进行争抢，那些没抢到的进程都是白取了一次任务，这是浪费。
可以考虑使用 lua scripting 来优化一下这个逻辑，将 zrangebyscore 和 zrem 一同挪到服务器端进行原子化操作，
这样多个进程之间争抢任务时就不会出现这种浪费了。

参考[有赞延时队列设计](youzan_delay_queue_design.md)




