---
title: 读《Redis设计与实现》
date: '2023-03-20'
weight: 284100159
primary_category: reading-category
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247485404&idx=1&sn=07b72d623f5fc9a1d4d174baccdaea7b&chksm=a6c76b3191b0e22730aeb9d597f08c0240791ffa3801ceb8f49ff14d1b09b6f5459569d349fa
---

### 一、为什么读这本书？

在我开发的一个小应用中，某些数据的更新频率很低，但查询很复杂。我想要给它们加上缓存，不要每次都去MySQL中执行一段很复杂的SQL。

开发过程中我有一个疑问：缓存存活多长时间比较合适，1分钟，10分钟还是1小时？

当时我对Redis的理解，还只是Django中的简单使用：
    
    
    # 1. 在settings中配置Redis的链接  
    CACHES = {  
        'default': {  
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',  
            'LOCATION': 'redis://:password@127.0.0.1:6379',  
        }  
    }  
      
    # 2. 接着就可以使用了  
    from django.core.cache import cache  
    cache.set(key, 'xxx')  
    cache.get(key)  
    

我对自己的疑问并没有好的思考方向，于是决定**先对Redis了解多一些** 。

经过一番搜索，找到一本大家都很推荐的《Redis设计与实现》读了起来。

### 二、阅读本书的方式

阅读本书之前，我先在本地用`docker`起了一个Redis容器，且从GitHub上将源码拷贝下来。
    
    
    # 1.1 使用docker启动  
    docker run --name local-redis -d redis  
    # 1.2 设置一个密码：1234567  
    config set requirepass 1234567  
      
    # 2.1 拷贝代码  
    git clone https://github.com/redis/redis.git  
    # 2.2 将分支切换到与docker一致  
    git checkout 7.0.9  
    

上面docker指令启动的是最新版本的Redis，当前最新版本的Redis为7.0.9。

读书过程中，我将书中出现的大部分指令都在本地Redis客户端执行一遍，且会就书中提到的各个模块的实现细节——文件、struct与函数——都去源码中找一找并简单看看。

书中出现的指令，在最新版的Redis客户端中都能执行。

书中绝大部分内容，都能在最新版本源码中找到。

不过由于版本的变迁，书中内容与当前最新版本也会存在一些差异。

例如书中提到的：

> 除非在脚本中使用math.randomseed显式地修改seed，否则每次运行脚本时，Lua环境都使用固定的math.randomseed（0）语句来初始化seed。

我的测试结果是，每次运行脚本产生的随机值并不一样。说明Lua环境不再使用固定的math.randomseed（0）语句来初始化seed。

再例如：`typedef struct redisClient`去掉了`redis`前缀变为`typedef struct client`。

还有一些其它差异，并不于此处赘述，一切表现都将以使用版本为准。

### 三、本书的主要内容

本书分为4部分：

  * 数据结构与对象，介绍Redis的5种不同类型的对象，剖析这些对象所使用的底层数据结构，并说明这些数据结构是如何深刻地影响对象的功能和性能的。
    * 字符串对象
    * 列表对象（list object）
    * 哈希对象（hash object）
    * 集合对象（set object）
    * 有序集合对象（sorted set object）
  * 单机数据库的实现，对Redis实现单机数据库的方法进行了介绍。包含了持久化、事件、客户端、服务端等。
  * 多机数据库的实现，对Redis的Sentinel、复制（replication）、集群（cluster）三个多机功能进行了介绍。
  * 独立功能的实现，各个相对独立的功能模块进行了介绍。包括发布订阅、事务、Lua脚本、排序、二进制位数组、慢查询日志、监视器等。



以上内容摘抄自书中引言部分，具体内容不再搬运，大家有感兴趣的部分，可以直接上《微信读书》上面阅读。

这书是免费卡可读的。

### 四、读完本书的收获？

本书29万字，读完耗时17小时。

读完本书，我想我知道了就疑问“缓存存活多长比较合适”的思考方向。书中有一段是这样说的：

> Redis服务器中有不少功能需要获取系统的当前时间，而每次获取系统的当前时间都需要执行一次系统调用，为了减少系统调用的执行次数，服务器状态中的unixtime属性和mstime属性被用作当前时间的缓存。
> 
> 因为serverCron函数默认会以每100毫秒一次的频率更新unixtime属性和mstime属性，所以这两个属性记录的时间的精确度并不高。

100毫秒即0.1秒，Redis认为0.1秒已经是一个很长的时间，所以1分钟（600个0.1秒）已经可以算是一个比较长的存活时间。缓存存活1分钟，并不算短的。（当然，具体缓存多久，还是得根据实际的业务需求考量。）

读完本书，我能够用Redis客户端去查看缓存相关的内容，而不再像读本书前的一无所知。即便当前使用Redis指令依然不够熟练，需要对照着《Redis命令参考》来操作，但我终于敢说：“我知道Redis是什么了。”

Redis是什么？Redis是一个缓存数据库，存在里面的数据，能够被快速访问。

### 五、使用过的指令

读书当时，有很多感觉生疏的指令，我将其做了些整理，摘抄到此处作为本篇读书笔记的一部分：
    
    
    # 进入Redis cli  
    redis-cli -h 127.0.0.1 -p 6379 -a 1234567  
      
    # 使用redis-cli -a password总是提醒不安全  
    # 原来是可以进去之后再验证密码的  
    # redis-cli  
    # auth [username] password  
      
    # 查看某个key是什么类型  
    object encoding one  
      
    # 查看key所占用的内存大小（num1中只有一个1）  
    memory usage num1  
    # 输出：56  
      
    # Redis cli中也是可以执行脚本的  
    # 下面指令创建了一个名叫intergers的list，内容为1到512的数字  
    EVAL "for i=1, 512 do redis.call('rpush', KEYS[1], i) end" 1 "intergers"  
      
    # 载入脚本，如果脚本数据一致，生成的SHA1校验和也是一致的  
    script load "return 'hello world'"  
      
    # pattern是可以使用正则的  
    keys x*  
      
    # od 可以以ASCII码或是16进制展示文件  
    od dump.rdb  
      
    # 批量删除  
    redis-cli -n 2 -a 1234567 keys "aa*" | xargs redis-cli -n 2 -a 1234567 del  
      
    # 可以使用这个指令，猜测一下当前某些缓存的使用情况  
    OBJECT IDLETIME key  
      
    # info指令可以查看许多关于数据库的信息  
    info [section]  
      
    # 创建一个从服务器  
    # 1. 新起一个redis服务器，需要添加主服务器的密码（也可以配置在conf中）  
    redis-server --port 12345 --masterauth 1234567  
    # 2. 登录进去新的redis服务器，然后让它变成原来的从服务器  
    redis-cli -p 12345  
    slaveof 127.0.0.1 6379  
      
    # 对自己认主，可以去掉主从关系，不过需要重启服务才能生效  
    slaveof 127.0.0.1 12345  
      
    # 排序  
    sadd fruit apple banana cherry  
    mset apple-price 8 banana-price 5.5 cherry-price 7  
    sort fruit by *-price  
    

最后，再引用一段侯捷老师说过的话作为本篇结束语：

> 从事写作，有一件事非常要紧，就是资料的收集与整理。我所认识的一些有点成绩的朋友，他们都有自己一套收集整理数据的系统，他们都深知这件事情的重要性。一百份整理过的数据，价值高于一万份未经整理的资料；未经自己整理的资料，和垃圾没有两样。

阅读本书时，我再次感受到这观点的正确性：只有自己整理且维护目录的资料，才能被得心应手的选用。

### 六、引用链接

1、一个可视化数据查看工具，可以直观的看到数据内容与大小：https://github.com/qishibo/AnotherRedisDesktopManager/releases

2、info指令的详细介绍：https://www.runoob.com/redis/server-info.html

3、Redis 命令参考：http://doc.redisfans.com/

↓↓↓欢迎关注
