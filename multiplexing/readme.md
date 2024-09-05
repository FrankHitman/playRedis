# Multiplexing 多路复用通讯

## Redis是单线程的，但是为什么I/O吞吐率那么高？

官网文档给的解释是：

- 通常完成一个redis的请求所需的时间短，例如 get， put；当然也有些耗时的命令，比如 sort排序，lrem 删除多个，sunion 集合合并。
- but primarily because these products are designed to not block on system calls, such as reading data from or writing
  data to a socket. 不阻塞系统调用，
  Redis的I/O多路复用程序的所有功能是通过包装select、epoll、evport和kqueue这些I/O多路复用函数库来实现的

## multiplexing
- Redis 服务端与客户端的连接是持久的，与 HTTP RESTful API 每次请求都要经历：建立连接-通讯-销毁连接的操作，因此可以节省资源。
- 管理Redis网络连接的三种流派：
  - Unmanaged 丢给客户自己处理，例如 node_redis library
  - Pooled 连接池，例如 jedis
  - Multiplexed：例如 StackExchange.Redis for the .NET In multiplexing, you take many threads and share a single 
    connection. 
  
multiplexing（只使用一个 client-server connection）优点
- 可以处理大量的线程的请求，而不需要创建和销毁连接
- 不用像连接池那样，需要考虑从池子中获取和归还连接
- 隐形的管道，一次request携带多条命令，这些命令会顺序执行

multiplexing（只使用一个 client-server connection）缺点
- 慢操作 Client-blocking operations，要么执行成功，要么超时结束
  - blpop 阻塞获取队列，队列空时候会一致阻塞，直到有元素被push进队列
  - brpop
  - brpoplpush
  - bzpopmin
  - bzpopmax
  - xread_block
- 发送或者获取大尺寸数据也会阻塞connection的
- 

[single-threaded-nature-of-redis](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/#single-threaded-nature-of-redis)
[彻底搞懂Redis的线程模型](https://juejin.cn/post/6844903970511519758)
[multiplexing-explained](https://redis.io/blog/multiplexing-explained/)