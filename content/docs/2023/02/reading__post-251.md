---
title: 一段关于“条件变量”的长期记忆
date: '2023-02-26'
weight: 284320251
primary_category: reading
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247485366&idx=1&sn=0c8cca0404bf01d58a92ccc41b5db513&chksm=a6c76b5b91b0e24d7900cf401dc8ece1a0aab0e149e88bfdc412a1cf226ab33c15cd7c92851b
---
一直以来，我对进程与线程的理解都是模糊的。进程是操作系统运行的基本单位？线程由进程管理，一个进程里面可以有多个线程？线程间的通信是怎样的？进程间的通信呢？线程和进程，到底是什么？

这些老生常谈的问题，我翻过很多的博客，看过很多的阐述，但是一直记不住。有些当时记住过，但过段时间又忘记了。

我想将它们理解的清楚一些，于是在《微信读书》上找来《操作系统导论》读起来。（是的，使用手机看技术书，能够降低持续阅读的门槛。我用电脑看《[数据库系统概论](http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247485013&idx=1&sn=6d00597498bc6da952e90fbda2b255dc&chksm=a6c76ab891b0e3aec82efa3912dabd3365fa95d78385def60eb1e475b0e25b057ec99c41314a&scene=21#wechat_redirect)》，一年半过去，才刚看到一半。）

《并发》部分《条件变量》一章中，一段“使用条件变量让父线程等待子线程”的代码，在我看第三遍时才想明白逻辑含义。想清楚瞬间我想着为“条件变量”输出一篇更新，使得它成为我永不会忘记的“长期记忆”，于是有了本篇。

（这过程中，有一种神奇的心理变化：

  1. 全不了解X但想要弄懂X是什么时：“这东西真的高端，好牛啊。等我弄懂了必须写一篇博客。”
  2. 开始理解X时：“哎呀，这个真的好难，我怎么就没有想到呢，和大佬的差距这么大？博客有了有了。”
  3. 真正搞清楚X是什么时：“这个这么简单，好像没什么好写的。”
  4. 到尝试为X写一篇更新时：“怎么写？怎么写？怎么写？”



此处的X指的是下面的一段代码。X代表的对象，可以有很多，比如“Django的使用”“炒回锅肉”“介绍一条爬山路径”等等等等。）

这段代码是这样的：
    
    
    pthread_cond_wait(pthread_cond_t *c, pthread_mutex_t *m);   
    pthread_cond_signal(pthread_cond_t  *c);  
      
    int done = 0;  
    pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;  
    pthread_cond_t c = PTHREAD_COND_INITIALIZER;  
      
    void thr_exit() {  
        Pthread_mutex_lock(&m);  
        done = 1;  
        Pthread_cond_signal(&c);  
        Pthread_mutex_unlock(&m);  
     }  
      
    void *child(void *arg) {  
         printf("child\n");  
         thr_exit();  
         return NULL;  
    }  
      
    void thr_join() {  
        Pthread_mutex_lock(&m);  
        while (done == 0)  
            Pthread_cond_wait(&c, &m);  
        Pthread_mutex_unlock(&m);  
    }  
      
    int main(int argc, char *argv[]) {  
        printf("parent: begin\n");  
        pthread_t p;  
        Pthread_create(&p, NULL, child, NULL);  
        thr_join();  
        printf("parent: end\n");  
        return 0;  
    }  
    

看第一遍时，我对thr_join中while(done==0)的猜想是：Pthread_cond_wait之后会立马执行后面的Pthread_mutex_unlock操作。

我按照这理解继续阅读，一直感觉不太对：wait的作用不是让线程睡眠么？那睡眠不就是立马停下来？怎么可能会执行后面的代码？

感觉不太对后，我回过头来再看一遍这代码，依然糊里糊涂的：怎么回事？它没有解锁怎么能够停下来呢？岂不是会一直死在这里？

直到第三遍，再一字一句的将书中描述：

> 条件变量有两种相关操作：wait()和signal()。线程要睡眠的时候，调用wait()。当线程想唤醒等待在某个条件变量上的睡眠线程时，调用signal()。
> 
> ……
> 
> 我们常简称为wait()和signal()。你可能注意到一点，wait()调用有一个参数，它是互斥量。它假定在wait()调用时，这个互斥量是已上锁状态。wait()的职责是释放锁，并让调用线程休眠（原子地）。当线程被唤醒时（在另外某个线程发信号给它后），它必须重新获取锁，再返回调用者。这样复杂的步骤也是为了避免在线程陷入休眠时，产生一些竞态条件。

认真过一遍后才真正理解书中意思：

我之前的理解——调用wait之后会继续执行后面的unlock——是错误的。真正做unlock操作的，是wait()。

调用wait()时，线程确实是在此处立即休眠了，后面的代码将不再执行。休眠的同时，wait()会把锁释放，保证其它线程（即thr_exit）可以获得锁执行。

当signal()被调用之后，wait()收到信号并重新上锁，接着进入while循环发现done已经不是0，跳出循环，执行unlock()，thr_join函数执行完毕。（此处while改为if也能得到正确效果。作者说，使用while总是好的，它能让线程在收到信号后能够立即执行。）

此段代码，在子线程创建后可能有两种执行顺序：先执行子线程、或是先执行主线程。要想清楚两种情况，需要想两遍。  


造成理解困难，我想主要有两个原因：

  1. 一是对多线程切换的流程不够熟悉，即便生活中有“烧水时洗菜、煲汤时剥蒜”的“多线程”场景，但更多场景是同时只做一件事的，对这种概念的训练不够多，何况还要将其代入到计算机“虚拟”世界。（“我炒菜阿妮剥蒜”是“多进程”；计算机多线程做的事情并非“虚拟”，只是速度快到我难以想象，计算单元小到我看不见。）
  2. 二是对“条件变量”的陌生，我不知道条件变量是如何实现的。上面的代码，其实封装性很高，wait()和signal()做的事情很多。



书中只是简单提到条件变量的底层实现：

> 线程可以使用条件变量（condition variable），来等待一个条件变成真。条件变量是一个显式队列，当某些执行状态（即条件，condition）不满足时，线程可以把自己加入队列，等待（waiting）该条件。另外某个线程，当它改变了上述状态时，就可以唤醒一个或者多个等待线程（通过在该条件上发信号），让它们继续执行。

条件变量，是并发程序设计的原语之一，与它有相同地位的还有“锁”。当然，还有“信号量”……

写到此处，我依然对线程、进程缺乏一个框架性的认识，但至少多了些想法：“两个线程同时执行，你要等我我要等你，让我们给彼此一个条件变量，待会见吧。” <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247485366&amp;idx=1&amp;sn=0c8cca0404bf01d58a92ccc41b5db513&amp;chksm=a6c76b5b91b0e24d7900cf401dc8ece1a0aab0e149e88bfdc412a1cf226ab33c15cd7c92851b" rel="noopener noreferrer">原文链接</a>）</small>