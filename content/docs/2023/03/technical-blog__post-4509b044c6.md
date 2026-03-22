---
title: 月更 | 一篇技术文的翻译：Python生成器的实现
date: '2023-03-26'
weight: 284044509
primary_category: technical-blog
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247485444&idx=1&sn=5f85cabba348964ddb89fa857a71f86e&chksm=a6c764e991b0edff26de0723a958b74fb59b2864982e8d6de73059a0483dc6a1b3604b2a7b19
---
### 一、起念

最近在看一本关于 Python 基础知识的书，书名叫 Effective Python (2nd Edition)。正看到第32小节：Consider Generator Expressions for Large List Comprehensions（当列表推导式很大时，考虑使用生成器）。

这一节中提到：

> Generator expressions don’t materialize the whole output sequence when they’re run. Instead, generator expressions evaluate to an iterator that yields one item at a time from the expression. （生成器表达式在执行时不会一次性生成全部的返回结果，它会产生一个迭代器，一次只输出一个结果。）

当程序使用大列表时，内存可能会爆，作者推荐：**尽量使用生成器** 。

我想知道为什么生成器会有省内存的效用？

于是去寻找答案，我找到答案，答案是一篇博客。

现将其译为中文，分享给大家。

### 二、译文

理解 Python 生成器之前，需要先弄清楚普通 Python 函数是如何工作的。一般来说，当一个 Python 函数调用子函数，子函数在返回（或抛出异常）之前都将对流程保有控制权。返回（或抛出异常）之后，再将控制权还给上层调用者。
    
    
    >>> def foo():  
    ...     bar()  
    ...  
    >>> def bar():  
    ...     pass  
    

标准 Python 解释器是用 C 实现的。执行 Python 函数的 C 函数叫做 `PyEval_EvalFrameEx`。它持有 Python 的栈帧对象，并在当前上下文中执行 Python 的字节码。`foo`函数的字节码如下（各个位置的含义请看[之前的整理](http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484164&idx=2&sn=510e41c23cbd44428e9f7f53f35eebab&chksm=a6c76fe991b0e6ff2ba9699efe963b9a0afa456b35f837ec902a0ba7719103862ee23f4a51c3&scene=21#wechat_redirect)）：
    
    
    >>> import dis  
    >>> dis.dis(foo)  
      2           0 LOAD_GLOBAL              0 (bar)  
                  2 CALL_FUNCTION            0  
                  4 POP_TOP  
                  6 LOAD_CONST               0 (None)  
                  8 RETURN_VALUE  
    

`foo`函数将`bar`函数加载到它的栈中并调用它，然后将它的返回值从栈中弹出来，把`None` 载入栈中，然后再返回`None`。

当`PyEval_EvalFrameEx`遇见`CALL_FUNCTION`时，它创建一个新的 Python 栈帧并递归调用：即`PyEval_EvalFrameEx`带着新的包含`bar`函数所有信息的新的栈帧递归调用它自己。

**明白 Python 的栈帧是在堆内存中是很重要的！** Python 解释器只是一个普通的 C 程序，所以它的栈帧就是普通的栈帧。但是 Python 的栈帧是被这个 C 程序在堆上操作的。除了一些特殊情况外，这意味着 Python 的栈帧可以在函数调用之外存活。为了直观地说明这个问题，让我们来看看`bar`函数执行时的栈帧：
    
    
    >>> import inspect  
    >>> frame = None  
    >>> def foo():  
    ...     bar()  
    ...  
    >>> def bar():  
    ...     global frame  
    ...     frame = inspect.currentframe()  
    ...  
    >>> foo()  
    >>> # 当前帧正在执行'bar'的代码  
    >>> frame.f_code.co_name  
    'bar'  
    >>> # 当前帧的父节点，指向了'foo'  
    >>> caller_frame = frame.f_back  
    >>> caller_frame.f_code.co_name  
    'foo'  
    >>> # 栈帧的类型  
    >>> type(frame)  
    <class 'frame'>  
    >>> type(frame.f_back)  
    <class 'frame'>  
    

<figure class="figure-with-caption">
<img src="/images/wechat/4509b044c6d9/001.png" alt="图片" loading="lazy" decoding="async" />
<figcaption>函数调用</figcaption>
</figure>

如上，实现生成器的舞台——代码对象和栈帧——已经搭建好了。

下面是一个生成器函数：
    
    
    >>> def gen_fn():  
    ...     result = yield 1  
    ...     print(f'result of yield: {result}')  
    ...     result2 = yield 2  
    ...     print(f'result of 2nd yield: {result2}')  
    ...     return 'done'  
    ...  
    

当 Python 将`gen_fn`编译为字节码时，编译器看到`yield`关键字后知道`gen_fn`是一个生成器函数，它会在函数身上设置一个标记：
    
    
    >>> # generator 的标志位在第5位  
    >>> # Python源码中定义：#define CO_GENERATOR    0x0020  
    >>> generator_bit = 1 << 5  
    >>> bin(generator_bit)  
    '0b100000'  
      
    >>> bool(gen_fn.__code__.co_flags & generator_bit)  
    True  
    >>> bool(bar.__code__.co_flags & generator_bit)  
    False  
    

一个生成器函数被调用时，Python 会看到生成器标识，此时并不会真的执行这个函数，而是创建一个生成器：
    
    
    >>> gen = gen_fn()  
    >>> type(gen)  
    <class 'generator'>  
    

Python 生成器将栈帧以及对一些代码的引用封装在一起。`gen_fn`的内容为：
    
    
    >>> gen.gi_code.co_name  
    'gen_fn'  
    

所有来自于`gen_fn`的生成器都指向相同代码。但每一个都保有自己的独立栈帧。这个栈帧并不在真正的栈上，而是待在堆内存中等待着下次被使用：

<figure class="figure-with-caption">
<img src="/images/wechat/4509b044c6d9/002.png" alt="图片" loading="lazy" decoding="async" />
<figcaption>生成器内存布局</figcaption>
</figure>

帧对象有一个叫做`last instruction`的指针，指向最近执行的指令位置（译注：此处就是代码中`yield`所在地方）。最开始`last instruction`的值为 -1，代表这个生成器还未开始执行：
    
    
    >>> gen.gi_frame.f_lasti  
    -1  
    

当我们调用`send`，生成器到达它的第一个`yield`，然后停下来。`send`的返回值为 1，来自于`gen`传递给`yield`表达式的值：
    
    
    >>> gen.send(None)  
    1  
    

现在生成器的`last instruction`指向编译后总长度为46的字节码的第4位（此处我的测试与原文有些差异，原文总长度为56）：
    
    
    >>> gen.gi_frame.f_lasti  
    4  
    >>> len(gen.gi_code.co_code)  
    46  
    

生成器可以被任何函数在任何时间重新唤醒，因为它的栈帧在堆内存中，并非真的在栈空间中。它的调用阶层并非是固定的，它不用遵守普通函数的先进后出规则。

生成器，像云一样自由~

我们可以再将 "hello" 传递给生成器，它会成为`yield`语句的返回值，然后生成器继续执行，直到将2返回：
    
    
    >>> ret = gen.send('hello')  
    result of yield: hello  
    >>> ret  
    2  
    

现在栈帧中包含局部变量`result`:
    
    
    >>> gen.gi_frame.f_locals  
    {'result': 'hello'}  
    

其它被`gen_fn`创建的生成器都会有它们自己的栈帧和局部变量。

当我们再一次调用`send`，生成器从它的第二个`yield`语句继续下去，以它特有的`StopIteration`异常结束。
    
    
    >>> ret = gen.send('bye')  
    result of 2nd yield: bye  
    Traceback (most recent call last):  
      File "<stdin>", line 1, in <module>  
    StopIteration: done  
    

这个异常包含了一个值，这个值来自于生成器的返回值：字符串`done`。

### 三、结论

为什么生成器能够节省内存呢？

待我将上面翻译部分来回读两三遍后，才发现答案其实就在书中：生成器一次只处理一个值、只生成一个结果，处理完毕并不会将结果存着；既然如此，不需要申请很多内存来保存所有的结果，那肯定省内存嘛。

至于生成器是如何做到一次只处理一个值的呢？

因为生成器函数执行时，只要碰到`yield`就停下来，等待下一个`next`的触发。一碰到`yield`就停下来，等待`next`信号继续。

函数调用如何能够停下来？

是因为大部分Python函数的栈帧都保存在堆内存上，不用遵守“先进后出”规则。

### 四、参考链接

<figure class="figure-with-caption">
<img src="/images/wechat/4509b044c6d9/003.png" alt="图片" loading="lazy" decoding="async" />
<figcaption>一张来自于《操作系统导论》关于堆和栈的图</figcaption>
</figure>

1、原文链接：http://aosabook.org/en/500L/a-web-crawler-with-asyncio-coroutines.html （How Python Generators Work小节）

2、Frame Object的介绍：https://nanguage.gitbook.io/inside-python-vm-cn/6.-frames-objects

3、`yield` 关键词的讲解，这里面有很多的大神清楚讲解：https://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do-in-python/231855#231855 <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247485444&amp;idx=1&amp;sn=5f85cabba348964ddb89fa857a71f86e&amp;chksm=a6c764e991b0edff26de0723a958b74fb59b2864982e8d6de73059a0483dc6a1b3604b2a7b19" rel="noopener noreferrer">原文链接</a>）</small>