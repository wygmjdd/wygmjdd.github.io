---
title: Python字节码生成
date: '2021-03-28'
weight: 291320028
primary_category: technical-blog
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247483970&idx=1&sn=dd3a2d00fecf5caf0b79e2262d8b3d4b&chksm=a6c76eaf91b0e7b9a0d5eb293e75e27a38a820a00db9504fbbc71e74ba60d487e248d6995ba6
---
学习“Python函数调用”过程中，经常的需要生成一段字节码。每一次生成，我都需要照着上次的笔记，才能敲出简单的几行生成代码，这让我感到有点羞耻。

我要把这个流程，记在脑子里！

## 字节码生成流程

### Python源文件

此前为了测试闭包，创建了一个名为closure.py的Python文件。
    
    
    # -*- coding: utf-8 -*-  
      
    def get_func():  
    	value = "inner"  
      
    	def inner_func():  
    		print(value)  
      
    	return inner_func  
      
      
    show_value = get_func()  
    show_value()  
    

### 生成字节码的代码
    
    
    s = open('closure.py').read()  
    co = compile(s, 'closure.py', 'exec')  
    import dis  
    dis.dis(co)  
    

### 字节码

于closure.py文件所在目录，打开cmd（在Windows下面测试），敲入**py -2** ，依次执行上述生成代码，得到以下结果：
    
    
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
    

## 生成过程详述

### 一、读取文件
    
    
    s = open('closure.py').read()  
    

如果要得到字节码，是需要先有代码的。代码被保存在文件中，读取一下。使用open函数的默认配置，将文件读进内存中，得到一个file对象，file对象被read之后，得到str，str中存储着closure.py中的代码。

当然，代码可以不止是文件，只要是一个保存了代码的str对象，就ok的。这str对象可以来自于：

  * Python文件。

  * 直接在Python交互式解释器中敲的。

  * 网络传输。




### 二、编译文件
    
    
    co = compile(s, 'closure.py', 'exec')  
    

内存中有了代码，字节码怎么来呢？调用build-in函数compile，编译一下，编译的结果为code object（或者是AST object，暂不研究）。
    
    
    compile(source, filename, mode, flags=0, dont_inherit=False, optimize=- 1)  
    

compile函数必须传递3个参数：

  * source，第一步中的str（也可以是byte string、AST object）。

  * filename，来源文件的文件名。如果没有，哈，随便给一个也可以。

  * mode，'exec'、'eval'和'single'三选一，一系列语句用'exec'，单一表达式用'eval'，单个交互式语句用'single'。




剩下的3个参数（只摘抄一下）：

> 可选参数 flags 和 dont_inherit 控制应当激活哪个编译器选项以及应当允许哪个future 特性。
> 
> optimize 实参指定编译器的优化级别；默认值 -1 选择与解释器的 -O 选项相同的优化级别。显式级别为 0 （没有优化；debug 为真）、1 （断言被删除， debug 为假）或 2 （文档字符串也被删除）。

### 三、反汇编
    
    
    import dis  
    dis.dis(co)  
    

dis函数将编译器和解释器使用的字节码（CPython bytecode）作为输入，输出一种可以用来分析阅读的简单格式。也就是上面所看到的字节码。

dis函数的输入种类可以有很多：

> a module, a class, a method, a function, a generator, an asynchronous generator, a coroutine, a code object, a string of source code or a byte sequence of raw bytecode. （模块、类、方法、函数、生成器、异步生成器、协程、代码对象、代码字符、字节码。）

## 寻找嵌套的函数

以上，字节码的生成流程，便牢牢地刻在脑中。但细看上述字节码，get_func和inner_func去哪儿了？

经过一番探索，原来在编译出来的code对象中，有一个co_consts的成员，它是一个保存常量（constants used）的list。通过co_consts一层一层地往下翻，能够找到所有函数的code object：
    
    
    >>> dir(co)  
    ['__class__', '__cmp__', '__delattr__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__le__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'co_argcount', 'co_cellvars', 'co_code', 'co_consts', 'co_filename', 'co_firstlineno', 'co_flags', 'co_freevars', 'co_lnotab', 'co_name', 'co_names', 'co_nlocals', 'co_stacksize', 'co_varnames']  
    >>> co.co_consts  
    (<code object get_func at 00000000039B8C30, file "closure.py", line 3>, None)  
    >>> co.co_consts[0].co_consts  
    (None, 'inner', <code object inner_func at 00000000039B89B0, file "closure.py", line 6>)  
    >>> dis.dis(co.co_consts[0].co_consts[2])  
      7           0 LOAD_DEREF               0 (value)  
                  3 PRINT_ITEM  
                  4 PRINT_NEWLINE  
                  5 LOAD_CONST               0 (None)  
                  8 RETURN_VALUE  
    >>> co.co_consts[0].co_consts[2]  
    <code object inner_func at 00000000039B89B0, file "closure.py", line 6>  
    

但这样一层一层地找，依然是麻烦的。

有一个简单办法，直接在最新的Python3环境下调用dis.dis，它会把所有的内容都展现出来。
    
    
      3           0 LOAD_CONST               0 (<code object get_func at 0x000001335C5DF240, file "closure.py", line 3>)  
                  2 LOAD_CONST               1 ('get_func')  
                  4 MAKE_FUNCTION            0  
                  6 STORE_NAME               0 (get_func)  
      
     12           8 LOAD_NAME                0 (get_func)  
                 10 CALL_FUNCTION            0  
                 12 STORE_NAME               1 (show_value)  
      
     13          14 LOAD_NAME                1 (show_value)  
                 16 CALL_FUNCTION            0  
                 18 POP_TOP  
                 20 LOAD_CONST               2 (None)  
                 22 RETURN_VALUE  
      
    Disassembly of <code object get_func at 0x000001335C5DF240, file "closure.py", line 3>:  
      4           0 LOAD_CONST               1 ('inner')  
                  2 STORE_DEREF              0 (value)  
      
      6           4 LOAD_CLOSURE             0 (value)  
                  6 BUILD_TUPLE              1  
                  8 LOAD_CONST               2 (<code object inner_func at 0x000001335C5DF190, file "closure.py", line 6>)  
                 10 LOAD_CONST               3 ('get_func.<locals>.inner_func')  
                 12 MAKE_FUNCTION            8 (closure)  
                 14 STORE_FAST               0 (inner_func)  
      
      9          16 LOAD_FAST                0 (inner_func)  
                 18 RETURN_VALUE  
      
    Disassembly of <code object inner_func at 0x000001335C5DF190, file "closure.py", line 6>:  
      7           0 LOAD_GLOBAL              0 (print)  
                  2 LOAD_DEREF               0 (value)  
                  4 CALL_FUNCTION            1  
                  6 POP_TOP  
                  8 LOAD_CONST               0 (None)  
                 10 RETURN_VALUE  
    

## 参考资料

  1. https://docs.python.org/3.10/library/functions.html?highlight=open#open

  2. https://docs.python.org/3.10/library/functions.html?highlight=compile#compile

  3. https://docs.python.org/3.10/library/dis.html?highlight=dis dis#module-dis <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247483970&amp;idx=1&amp;sn=dd3a2d00fecf5caf0b79e2262d8b3d4b&amp;chksm=a6c76eaf91b0e7b9a0d5eb293e75e27a38a820a00db9504fbbc71e74ba60d487e248d6995ba6" rel="noopener noreferrer">原文链接</a>）</small>