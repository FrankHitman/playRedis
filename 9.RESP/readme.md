# RESP
RESP(Redis Serialization Protocol)

RESP 是 Redis 序列化协议的简写。它是一种直观的文本协议，优势在于实现异常简单，解析性能极好。

Redis 协议将传输的结构数据分为 5 种最小单元类型，单元结束时统一加上回车换行符号\r\n。

- 单行字符串 以 + 符号开头。
- 多行字符串 以 $ 符号开头，后跟字符串长度。
- 整数值 以 : 符号开头，后跟整数的字符串形式。
- 错误消息 以 - 符号开头。
- 数组 以 * 号开头，后跟数组的长度。

## 使用
### 客户端 -> 服务器
set author codehole会被序列化成下面的字符串。
```
set author codehole
=
*3\r\n$3\r\nset\r\n$6\r\nauthor\r\n$8\r\ncodehole\r\n
```
在控制台输出这个字符串如下，可以看出这是很好阅读的一种格式。
    
    *3
    $3
    set
    $6
    author
    $8
    codehole

### 服务器 -> 客户端
#### 数组响应
    
    127.0.0.1:6379> hset info name laoqian
    (integer) 1
    127.0.0.1:6379> hset info age 30
    (integer) 1
    127.0.0.1:6379> hset info sex male
    (integer) 1
    127.0.0.1:6379> hgetall info
    1) "name"
    2) "laoqian"
    3) "age"
    4) "30"
    5) "sex"
    6) "male"
这里的 hgetall 命令返回的就是一个数组，第 0|2|4 位置的字符串是 hash 表的 key，第 1|3|5 位置的字符串是 value，客户端负责将数组组装成字典再返回。
    
    *6
    $4
    name
    $6
    laoqian
    $3
    age
    $2
    30
    $3
    sex
    $4
    male

#### 嵌套
    
    127.0.0.1:6379> scan 0
    1) "0"
    2) 1) "info"
       2) "books"
       3) "author"
scan 命令用来扫描服务器包含的所有 key 列表，它是以游标的形式获取，一次只获取一部分。

scan 命令返回的是一个嵌套数组。数组的第一个值表示游标的值，如果这个值为零，说明已经遍历完毕。
如果不为零，使用这个值作为 scan 命令的参数进行下一次遍历。数组的第二个值又是一个数组，这个数组就是 key 列表。
    
    *2
    $1
    0
    *3
    $4
    info
    $5
    books
    $6
    author
    
## 补充
如果起服务时候配置了appendonly，那么可以看到appendonly.aof文件内就是RESP格式的数据，参考本目录下appendonly.aof文件
```shell script
docker run \
 -p 6379:6379 \
 -v $PWD/data:/data \
 --name redis \
 --restart=always \
 -d redis redis-server --appendonly yes  --requirepass "739e9ec7-efd7-4e21-b68b-c4a3807b448b" 
```
