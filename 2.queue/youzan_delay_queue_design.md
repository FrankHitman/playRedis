# Delay Queue Job Design

## 整体结构
整个延迟队列由4个部分组成：

- Job Pool用来存放所有Job的元信息。
- Delay Bucket是一组以时间为维度的有序队列，用来存放所有需要延迟的／已经被reserve的Job（这里只存放Job Id）。
- Timer负责实时扫描各个Bucket，并将delay时间大于等于当前时间的Job放入到对应的Ready Queue。
- Ready Queue存放处于Ready状态的Job（这里只存放Job Id），以供消费程序消费。
如下图表述： 
![Delay Queue](delay_queue.jpg)

## 基本概念
- Job：需要异步处理的任务，是延迟队列里的基本单元。与具体的Topic关联在一起。
- Topic：一组相同类型Job的集合（队列）。供消费者来订阅。
### 消息结构
每个Job必须包含一下几个属性：

- Topic：Job类型。可以理解成具体的业务名称。
- Id：Job的唯一标识。用来检索和删除指定的Job信息。
- Delay：Job需要延迟的时间。单位：秒。（服务端会将其转换为绝对时间）
- TTR（time-to-run)：Job执行超时时间。单位：秒。
- Body：Job的内容，供消费者做具体的业务处理，以json格式存储。

### 消息状态转换
每个Job只会处于某一个状态下：

- ready：可执行状态，等待消费。
- delay：不可执行状态，等待时钟周期。
- reserved：已被消费者读取，但还未得到消费者的响应（delete、finish）。
- deleted：已被消费完成或者已被删除。

下面是四个状态的转换示意图： 

![Job State Flow](job_state_flow.jpg)

### 消息存储
在选择存储介质之前，先来确定下具体的数据结构：

- Job Poll存放的Job元信息，只需要K/V形式的结构即可。key为job id，value为job struct。string/hash
- Delay Bucket是一个有序队列。SortedSet
- Ready Queue是一个普通list或者队列都行。list

能够同时满足以上需求的，非redis莫属了。
bucket的数据结构就是redis的zset，将其分为多个bucket是为了提高扫描速度，降低消息延迟。

## reference

- [youzan](https://tech.youzan.com/queuing_delay/)

- [delay-queue](https://github.com/ouqiang/delay-queue)

- [cron](https://github.com/robfig/cron)