# Transaction
    begin();
    try {
        command1();
        command2();
        ....
        commit();
    } catch(Exception e) {
        rollback();
    }
## 使用
Redis 事务指令有 multi/exec/discard。multi 指示事务的开始，exec 指示事务的执行，discard 指示事务的丢弃。

```shell script
Franks-Mac:playRedis frank$ redis-cli -p 6679
127.0.0.1:6679> 
127.0.0.1:6679> multi
OK
127.0.0.1:6679> incr book
QUEUED
127.0.0.1:6679> incr book
QUEUED
127.0.0.1:6679> exec
1) (integer) 1
2) (integer) 2
127.0.0.1:6679> exec
(error) ERR EXEC without MULTI
127.0.0.1:6679> 

```
所有的指令在 exec 之前不执行，而是缓存在服务器的一个事务队列中，服务器一旦收到 exec 指令，才开执行整个事务队列，
执行完毕后一次性返回所有指令的运行结果。因为 Redis 的单线程特性，它不用担心自己在执行队列的时候被其它指令打搅，
可以保证他们能得到的「原子性」执行

## 假的原子性
```shell script
127.0.0.1:6679> multi
OK
127.0.0.1:6679> set books pythoncookbook
QUEUED
127.0.0.1:6679> incr books
QUEUED
127.0.0.1:6679> set language java
QUEUED
127.0.0.1:6679> exec
1) OK
2) (error) ERR value is not an integer or out of range
3) OK
127.0.0.1:6679> get books
"pythoncookbook"
127.0.0.1:6679> get language
"java"
127.0.0.1:6679> 
```
上面的例子是事务执行到中间遇到失败了，因为我们不能对一个字符串进行数学运算，事务在遇到指令执行失败后，后面的指令还继续执行，
所以 poorman 的值能继续得到设置。

到这里，你应该明白 Redis 的事务根本不能算「原子性」，而仅仅是满足了事务的「隔离性」，隔离性中的串行化——当前执行的事务有着不被其它事务打断的权利。

## discard使用
```shell script
127.0.0.1:6679> set books 10
OK
127.0.0.1:6679> get books
"10"
127.0.0.1:6679> multi 
OK
127.0.0.1:6679> incr books
QUEUED
127.0.0.1:6679> incr books
QUEUED
127.0.0.1:6679> get books
QUEUED
127.0.0.1:6679> discard
OK
127.0.0.1:6679> 
127.0.0.1:6679> get books
"10"
127.0.0.1:6679> discard
(error) ERR DISCARD without MULTI
127.0.0.1:6679> 

```

## 优化网络IO
上面的 Redis 事务在发送每个指令到事务缓存队列时都要经过一次网络读写，当一个事务内部的指令较多时，需要的网络 IO 时间也会线性增长。
所以通常 Redis 的客户端在执行事务时都会结合 pipeline 一起使用，这样可以将多次 IO 操作压缩为单次 IO 操作

    pipe = redis.pipeline(transaction=true)
    pipe.multi()
    pipe.incr("books")
    pipe.incr("books")
    values = pipe.execute()

## 乐观锁watch
考虑到一个业务场景，Redis 存储了我们的账户余额数据，它是一个整数。现在有两个并发的客户端要对账户余额进行修改操作，
这个修改不是一个简单的 incrby 指令，而是要对余额乘以一个倍数。Redis 可没有提供 multiplyby 这样的指令。
我们需要先取出余额然后在内存里乘以倍数，再将结果写回 Redis。

这就会出现并发问题，因为有多个客户端会并发进行操作。我们可以通过 Redis 的分布式锁来避免冲突，这是一个很好的解决方案。
分布式锁是一种悲观锁，那是不是可以使用乐观锁的方式来解决冲突呢？

Redis 提供了这种 watch 的机制，它就是一种乐观锁。有了 watch 我们又多了一种可以用来解决并发修改的方法。 watch 的使用方式如下：
    
    while True:
        do_watch()
        commands()
        multi()
        send_commands()
        try:
            exec()
            break
        except WatchError:
            continue
watch 会在事务开始之前盯住 1 个或多个关键变量，当事务执行时，也就是服务器收到了 exec 指令要顺序执行缓存的事务队列时，
Redis 会检查关键变量自 watch 之后，是否被修改了 (包括当前事务所在的客户端)。如果关键变量被人动过了，
exec 指令就会返回 null 回复告知客户端事务执行失败，这个时候客户端一般会选择重试。

    watch key [key ...]

    127.0.0.1:6679> watch books
    OK
    127.0.0.1:6679> incr books
    (integer) 11
    127.0.0.1:6679> multi
    OK
    127.0.0.1:6679> incr books
    QUEUED
    127.0.0.1:6679> exec
    (nil)
    127.0.0.1:6679> 

Redis 禁止在 multi 和 exec 之间执行 watch 指令，而必须在 multi 之前做好盯住关键变量，否则会出错。

实现对余额的加倍操作。 watch.py


