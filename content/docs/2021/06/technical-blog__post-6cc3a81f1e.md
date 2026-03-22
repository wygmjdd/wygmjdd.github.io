---
title: Python字节码dis反汇编后，各个位置的含义
date: '2021-06-27'
weight: 290410006
primary_category: technical-blog
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484164&idx=2&sn=510e41c23cbd44428e9f7f53f35eebab&chksm=a6c76fe991b0e6ff2ba9699efe963b9a0afa456b35f837ec902a0ba7719103862ee23f4a51c3
---
在[字节码的生成](http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247483970&idx=1&sn=dd3a2d00fecf5caf0b79e2262d8b3d4b&chksm=a6c76eaf91b0e7b9a0d5eb293e75e27a38a820a00db9504fbbc71e74ba60d487e248d6995ba6&scene=21#wechat_redirect)中，我搞明白了dis如何展示字节码。

当“字节码”放在我面前的时候，我能猜到某些位置上的含义，但还有些位置猜不到。我想弄清楚，这些猜不到的部分，具体的含义。
    
    
      3           0 LOAD_CONST               0 (<code object get_func at 00000000034EA7B0, file "closure.py", line 3>)  
                  3 MAKE_FUNCTION            0  
                  6 STORE_NAME               0 (get_func)  
      
     12           9 LOAD_NAME                0 (get_func)  
                 12 CALL_FUNCTION            0  
                 15 STORE_NAME               1 (show_value)  
      
     13          18 LOAD_NAME                1 (show_value)  
                 21 CALL_FUNCTION            0  
                 24 POP_TOP  
                 25 LOAD_CONST               1 (None)  
                 28 RETURN_VALUE  
    

将上次Python2生成的字节码摘抄在这里，由此能够看出来，一条字节码由5个部分组成：

  * 一个数字，可以猜到，是行号；

  * 又一个数字，猜不到；

  * 一行字符串，猜得到，指令的名字；

  * 还有一个数字，看起来像是参数的个数；

  * 又一个括号包起来的字符串，具体的参数？




不过，从Python交互环境下面粘贴过来，在markdown中展现的内容，不止如此：

![图片](/images/wechat/6cc3a81f1ef6/001.png)

第一个数字和第二个数字中间，有3个小虚线，是否意味着这里面，还藏着2个不知名数据呢？

我找了几个很大的文件，反汇编了一下，发现中间只会多出一个符号“>>”，这个符号又是什么意思呢？
    
    
    574     >>  226 LOAD_CONST               4 ('')  
                228 STORE_FAST               6 (opt)  
    

以上，是我初次看到字节码所长的样子，并猜测着各个位置上的意思。

继续网上冲浪，寻找这字节码的各个位置含义。最终让我找到一篇超赞的文章，它让我理解了dis.dis(*args)所生成的结果。

事实上，dis生成结果只是Python为程序员所设计的易于理解的，反汇编（Disassembling ）之后的版本。每一条字节码本质上是由两个字节存储的一条指令，有以下形式：
    
    
    # 一个指令编号，后面跟着一个指令参数  
    opcode oparg   
    opcode oparg  
    

#### opcode（指令编号）

一个小于等于255的正整数，代表了具体指令是什么。它对应一个易于理解的opname，这个opname可以在两个地方看到：

  * Python源码中的Include/opcode.h文件；

  * dis模块的opname dict。



    
    
    import dis  
    print(dis.opname[101])          # 'LOAD_NAME'  
    

#### oparg（指令参数）

对应指令的参数，每一个参数，都根据opcode的不同，而拥有不同的意义。

有两个需要注意的点是：

  1. 有一些指令不需要参数，Python用编号来进行区分，小于dis.HAVE_ARGUMENT（Python3.9.1中是90）的指令没有参数，大于等于dis.HAVE_ARGUMENT的指令有参数。

  2. 另外一些指令，参数可能会大于255，1个字节存储不了，则会在该指令前再插入一条EXTENDED_ARG指令，辅助存储。每一条指令前，最多只能插入3条EXTENDED_ARG。



    
    
    // Python3.9.1\...\Objects\frameobject.c  
      
    // 真正arg的计算方式   
    /* Given the index of the effective opcode,  
       scan back to construct the oparg with EXTENDED_ARG */  
    static unsigned int  
    get_arg(const _Py_CODEUNIT *codestr, Py_ssize_t i)  
    {  
        _Py_CODEUNIT word;  
        unsigned int oparg = _Py_OPARG(codestr[i]);  
        if (i >= 1 && _Py_OPCODE(word = codestr[i-1]) == EXTENDED_ARG) {  
            oparg |= _Py_OPARG(word) << 8;  
            if (i >= 2 && _Py_OPCODE(word = codestr[i-2]) == EXTENDED_ARG) {  
                oparg |= _Py_OPARG(word) << 16;  
                if (i >= 3 && _Py_OPCODE(word = codestr[i-3]) == EXTENDED_ARG) {  
                    oparg |= _Py_OPARG(word) << 24;  
                }  
            }  
        }  
        return oparg;  
    }  
    

按照我的理解，oparg，只是一个偏移量，它根据opcode所属于的组，去对应的数据结构（co_consts、co_names、co_varnames、co_cellvars + co_freevars、co_lnotab等）中拿真正的数据。

根据以上的了解，我搞清楚了各个位置的意义：

  * 一个数字，是代码的行号；

  * 又一个数字，指令在字节码序列（co_code）中的偏移量；

  * 一行字符串，指令的名字；

  * 还有一个数字，oparg，指令的参数；

  * 又一个括号包起来的字符串，根据oparg取得的参数实际值；

  * 那个不常见的符号“>>”，标识循环（异常、if else判断等）的起止点。




## 参考资料

  1. 字节码的一篇介绍，https://opensource.com/article/18/4/introduction-python-bytecode

  2. 那一篇超赞的文章，建议阅读，https://towardsdatascience.com/understanding-python-bytecode-e7edaae8734d <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247484164&amp;idx=2&amp;sn=510e41c23cbd44428e9f7f53f35eebab&amp;chksm=a6c76fe991b0e6ff2ba9699efe963b9a0afa456b35f837ec902a0ba7719103862ee23f4a51c3" rel="noopener noreferrer">原文链接</a>）</small>




  


* * *