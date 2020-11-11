# LUA Script

## eval
```
# 分布式锁 del_if_equals
if redis.call("get",KEYS[1]) == ARGV[1] then
    return redis.call("del",KEYS[1])
else
    return 0
end
```

那上面这个脚本如何执行呢？使用 EVAL 指令
```
127.0.0.1:6379> set foo bar
OK
127.0.0.1:6379> eval 'if redis.call("get",KEYS[1]) == ARGV[1] then return redis.call("del",KEYS[1]) else return 0 end' 1 foo bar
(integer) 1
127.0.0.1:6379> eval 'if redis.call("get",KEYS[1]) == ARGV[1] then return redis.call("del",KEYS[1]) else return 0 end' 1 foo bar
(integer) 0
```

语法格式
```
eval script numkeys key [key ...] arg [arg ...]
#    脚本内容 key数量 每个key-value对
```
## script load & evalsha
mulby key value ==> $key = $key * value
```shell script
local curVal = redis.call("get", KEYS[1])
if curVal == false then
  curVal = 0
else
  curVal = tonumber(curVal)
end
curVal = curVal * tonumber(ARGV[1])
redis.call("set", KEYS[1], curVal)
return curVal
```
script load
```
127.0.0.1:6379> script load 'local curVal = redis.call("get", KEYS[1]); if curVal == false then curVal = 0 else curVal = tonumber(curVal) end; curVal = curVal * tonumber(ARGV[1]); redis.call("set", KEYS[1], curVal); return curVal'
"be4f93d8a5379e5e5b768a74e77c8a4eb0434441"
```
evalsha
```
127.0.0.1:6379> set foo 1
OK
127.0.0.1:6379> evalsha be4f93d8a5379e5e5b768a74e77c8a4eb0434441 1 foo 5
(integer) 5
127.0.0.1:6379> evalsha be4f93d8a5379e5e5b768a74e77c8a4eb0434441 1 foo 5
(integer) 25
```

## script file
```
$ cat mset.txt
return redis.pcall('mset', KEYS[1], ARGV[1], KEYS[2], ARGV[2])
$ cat mget.txt
return redis.pcall('mget', KEYS[1], KEYS[2])
$ redis-cli -p 6579 --eval mset.txt key1 key2 , value1 value2
OK
$ redis-cli -p 6579 --eval mget.txt key1  key2
1) "value1"
2) "value2"
```


