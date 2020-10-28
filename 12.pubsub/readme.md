# PubSub
## 消息多播
消息多播允许生产者生产一次消息，中间件负责将消息复制到多个消息队列，每个消息队列由相应的消费组进行消费。
它是分布式系统常用的一种解耦方式，用于将多个消费组的逻辑进行拆分。支持了消息多播，多个消费组的逻辑就可以放到不同的子系统中。

## PubSub使用
```
    subscribe channel [channel ...]
    publish channel message
    psubscribe pattern [pattern ...]
```
Redis单独使用了一个模块来支持消息多播，这个模块的名字叫着 PubSub，也就是 PublisherSubscriber，发布者订阅者模型。

执行 pubsub.py

    {'type': 'subscribe', 'pattern': None, 'channel': b'codehole', 'data': 1}           # 通知消息订阅成功
    None
    {'type': 'message', 'pattern': None, 'channel': b'codehole', 'data': b'java comes'}
    {'type': 'message', 'pattern': None, 'channel': b'codehole', 'data': b'python comes'}
    None

客户端发起订阅命令后，Redis 会立即给予一个反馈消息通知订阅成功。因为有网络传输延迟，在 subscribe 命令发出后，需要休眠一会，
再通过 get_message 才能拿到反馈消息。客户端接下来执行发布命令，发布了一条消息。同样因为网络延迟，在 publish 命令发出后，需要休眠一会，
再通过 get_message 才能拿到发布的消息。如果当前没有消息，get_message 会返回空，告知当前没有消息，所以它不是阻塞的。

Redis PubSub 的生产者和消费者是不同的连接，也就是上面这个例子实际上使用了两个 Redis 的连接。
这是必须的，因为 Redis 不允许连接在 subscribe 等待消息时还要进行其它的操作。

### 生产者-消费者
参考 producer.py和consumer.py，需先执行consumer.py再去执行producer.py。
因为redis不对消息持久化，如果先执行生产者，消息并不会存储在redis中，在接着执行消费者时候并不会接收到之前的消息。

    {'type': 'subscribe', 'pattern': None, 'channel': b'codehole', 'data': 1}
    {'type': 'message', 'pattern': None, 'channel': b'codehole', 'data': b'python comes'}
    {'type': 'message', 'pattern': None, 'channel': b'codehole', 'data': b'java comes'}
    {'type': 'message', 'pattern': None, 'channel': b'codehole', 'data': b'golang comes'}

- data 这个毫无疑问就是消息的内容，一个字符串。

- channel 这个也很明显，它表示当前订阅的主题名称。

- type 它表示消息的类型，如果是一个普通的消息，那么类型就是 message，如果是控制消息，比如订阅指令的反馈，它的类型就是 subscribe，如果是模式订阅的反馈，它的类型就是 psubscribe，还有取消订阅指令的反馈 unsubscribe 和 punsubscribe。

- pattern 它表示当前消息是使用哪种模式订阅到的，如果是通过 subscribe 指令订阅的，那么这个字段就是空。

上面的消费者是通过轮询 get_message 来收取消息的，如果收取不到就休眠 1s。这让我们想起了第 3 节的消息队列模型，
我们使用 blpop 来代替休眠一段时间来提高消息处理的及时性。

### 阻塞消费者
PubSub 的消费者如果使用休眠的方式来轮询消息，也会遭遇消息处理不及时的问题。
不过我们可以使用 listen 来阻塞监听消息来进行处理，这点同 blpop 原理是一样的。参考consumer_listen.py

其实是get_message和listen两个方法的不同，读一下redis-py中源码，listen方法返回的是一个生成器，
另外注意self.parse_response()调用参数 block=True 与 block=False, timeout=timeout 的区别。
```python
    def listen(self):
        "Listen for messages on channels this client has been subscribed to"
        while self.subscribed:
            response = self.handle_message(self.parse_response(block=True))
            if response is not None:
                yield response

    def get_message(self, ignore_subscribe_messages=False, timeout=0):
        """
        Get the next message if one is available, otherwise None.

        If timeout is specified, the system will wait for `timeout` seconds
        before returning. Timeout should be specified as a floating point
        number.
        """
        response = self.parse_response(block=False, timeout=timeout)
        if response:
            return self.handle_message(response, ignore_subscribe_messages)
        return None

```
```python
    def parse_response(self, block=True, timeout=0):
        "Parse the response from a publish/subscribe command"
        conn = self.connection
        if conn is None:
            raise RuntimeError(
                'pubsub connection not set: '
                'did you forget to call subscribe() or psubscribe()?')

        self.check_health()

        if not block and not conn.can_read(timeout=timeout):
            return None
        response = self._execute(conn, conn.read_response)

        if conn.health_check_interval and \
                response == self.health_check_response:
            # ignore the health check message as user might not expect it
            return None
        return response
```

## 模式订阅
使用正则匹配订阅多个主题
```shell script
127.0.0.1:6679> psubscribe codehole.*
Reading messages... (press Ctrl-C to quit)
1) "psubscribe"
2) "codehole.*"
3) (integer) 1
1) "pmessage"
2) "codehole.*"
3) "codehole.txt"
4) "hello"
1) "pmessage"
2) "codehole.*"
3) "codehole.jpg"
4) "world"
```

```shell script
127.0.0.1:6679> publish codehole hello
(integer) 0
127.0.0.1:6679> publish codehole.txt hello
(integer) 1
127.0.0.1:6679> publish codehole.jpg world
(integer) 1
```
可以看出publish后如果消息没有被订阅者就会返回0，被n个订阅者收到就会返回n

## PubSub 缺点
PubSub 的生产者传递过来一个消息，Redis 会直接找到相应的消费者传递过去。如果一个消费者都没有，那么消息直接丢弃。
如果开始有三个消费者，一个消费者突然挂掉了，生产者会继续发送消息，另外两个消费者可以持续收到消息。
但是挂掉的消费者重新连上的时候，这断连期间生产者发送的消息，对于这个消费者来说就是彻底丢失了。

如果 Redis 停机重启，PubSub 的消息是不会持久化的，毕竟 Redis 宕机就相当于一个消费者都没有，所有的消息直接被丢弃。

正是因为 PubSub 有这些缺点，它几乎找不到合适的应用场景。所以 Redis 的作者单独开启了一个项目 Disqueue 专门用来做多播消息队列。
该项目目前没有成熟，一直长期处于 Beta 版本，但是相应的客户端 sdk 已经非常丰富了，就待 Redis 作者临门一脚发布一个 Release 版本。

近期 Redis5.0 新增了 Stream 数据结构，这个功能给 Redis 带来了持久化消息队列，从此 PubSub 可以消失了，
Disqueue 估计也永远发不出它的 Release 版本了。