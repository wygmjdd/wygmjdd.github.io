---
title: 我的代码有几分？
date: '2020-11-07'
weight: 292730007
primary_category: technical-blog
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247483721&idx=1&sn=6f8d78eb3c334d5b1796098b8d15e981&chksm=a6c76da491b0e4b29f94f8c2101ac135909e6e4c40a10bf13915e62be74abeb0398ebc927071
---
最近做一个新功能，敲代码的过程中，有想法将代码敲的好看一些。于是在快完成的时候，使用pylint给代码打打分。我将整个试验过程进行了记录，为了某一天，公众号内容不知道更新什么的时候，展示一点我作为程序员的日常片段。

没想到这一天来的这么快。今天将跟公司团去三亚旅游，大概率今明两天不会有时间对许多半成品进行修改。便在各种记录中翻捡，找到此篇算是比较完整的内容。

* * *

使用pylint的默认配置检查结果如下：

> Your code has been rated at -17.35/10

没错，负分！就是负分！我看其中报的最多的是以下几种。

> C:314, 1: Variable name "xxData" doesn't conform to snake_case naming style (invalid-name)  
> 命名不符合snake_case规范。项目标准，统一风格。
> 
> E:815, 4: Undefined variable 'XXX' (undefined-variable)  
> 未定义变量。项目全局变量。
> 
> W:880, 0: Found indentation with tabs instead of spaces (mixed-indentation)  
> 使用了tab代替空格，但这还是我们项目标准，风格统一就好。

能否将上面这些项目检查去掉后，再进行一次评分呢？
    
    
    # 首先使用pylint生成一份默认的配置文件  
    pylint --generate-rcfile > myrc.pylintrc  
    

将myrc.pylintrc中进行一次查找替换，将snake_case替换为camelCase（不确定camelCase是否正确，需要确认一番）。  
在测试最后，看到注释中的文件名称被提示

> C: 1, 0: Module name "xx_xxx" doesn't conform to camelCase naming style (invalid-name)

我知道，我是拼正确了的。哈哈。

再使用指令
    
    
    pylint --rcfile myrc.pylintrc gift_center.py  
    

得到如下结果：

> Your code has been rated at -12.07/10 (previous run: -17.35/10, +5.28)

snake_case规范的报错都不再有，但是未定义变量依然占大头，继续找寻办法，将其干掉。在myrc.pylintrc中看见这么一段
    
    
    # Disable the message, report, category or checker with the given id(s). You  
    # can either give multiple identifiers separated by comma (,) or put this  
    # option multiple times (only on the command line, not in the configuration  
    # file where it should appear only once).You can also use "--disable=all" to  
    # disable everything first and then reenable specific checks. For example, if  
    # you want to run only the similarities checker, you can use "--disable=all  
    # --enable=similarities". If you want to run only the classes checker, but have  
    # no Warning level messages displayed, use"--disable=all --enable=classes  
    # --disable=W"  
    disable=print-statement,  
            parameter-unpacking,  
            ...  
            undefined-variable,      # 这一句是我新加的  
            mixed-indentation,       # 这一句还是我新加的  
    

忽然灵光一闪，似乎每一句检测结果后面都有一个小括号包起来的小写单词的，是否我将其加入到这里面就ok了呢？于是重新跑一遍，得到一个新的结果

> Your code has been rated at -1.57/10 (previous run: -12.07/10, +10.49)

将disable中再加入mixed-indentation跑一遍。哈哈哈，新的评分，已经变成正的了。

> Your code has been rated at 6.98/10 (previous run: -1.57/10, +8.55)

此时报错已经少了许多，但是输出的开头有许多此种报错。

> C: 15, 0: Wrong hanging indentation (add 3 spaces).

搜索了一下，还是缩进是tab的原因，于是再修改一下。
    
    
    # Number of spaces of indent required inside a hanging  or continued line.  
    indent-after-paren=4  
      
    # String used as indentation unit. This is usually "    " (4 spaces) or "\t" (1  
    # tab).  
    indent-string='    '  
      
    

改为如下样式
    
    
    indent-after-paren=1  
    indent-string='\t'  
    

分数增加一些，报错数量减少。

> C:190, 0: Wrong hanging indentation (add 7 spaces).
> 
> Your code has been rated at 7.22/10 (previous run: 6.98/10, +0.25)

应该是改对了地方，查看了一下报问题的代码位置。
    
    
    # C: 15, 0: Wrong hanging indentation (add 3 spaces).  
    TABLE_NAME = {  
    	"1": "xx",            # line no: 15  
    	# ...  
    	  
    # C:190, 0: Wrong hanging indentation (add 7 spaces).  
    	data = {  
    		"id": xxId,       # line no: 190  
    	# ...  
    

经过几次尝试之后，发现与indent-string无关，只是由indent-after-paren所报出来。好像报错中的(add 3 spaces)中的3，是缩进空格数 - 设定值。

啊，不知道具体为啥？先将这个问题放放，将一行文件大小改为160（默认为100）重跑一次。
    
    
    # Maximum number of characters on a single line.  
    max-line-length=160  
    

分数有点小小变化

> Your code has been rated at 7.48/10 (previous run: 6.98/10, +0.51)

再剩下的最多的报错就是

> C:854,14: More than one statement on a single line (multiple-statements)

来源于如下格式，但这种是我个人习惯哦，项目中并没有统一风格。
    
    
    def func():
    
        # ...  
    
    
        if a == b: return 'equal'  
    

于是暂时将它也去掉，干掉之后的得分来到

> Your code has been rated at 8.07/10 (previous run: 7.48/10, +0.59)

再干掉一个，并不需要每一个函数都添加docstring的。

> C:477, 0: Missing function docstring (missing-docstring)

分数来到

> Your code has been rated at 8.35/10 (previous run: 8.24/10, +0.11)

剩下的内容，除了Wrong hanging indentation之外，就都是需要修改的内容。好，让我来改一下。

> C:920, 4: Do not use `len(SEQUENCE)` to determine if a sequence is empty (len-as-condition)

不要使用len(seq)作为是否为空的判定，相关问题的讨论。

> C: 5, 0: standard import "import json" should be placed before "from xx.xxx import xx_method" (wrong-import-order)

改改import顺序。

> E: 5, 0: Unable to import 'xx.xx' (import-error)

这个是项目的，不管哦。

改完后的分数来到

> Your code has been rated at 8.66/10 (previous run: 8.35/10, +0.00)

  


上面那个缩进的，我觉得没什么问题，于是在disable选项中，再添加一项。最终的disable选项中添加内容
    
    
    disable=print-statement,  
            parameter-unpacking,  
            ...  
            undefined-variable,         # 项目变量  
            multiple-statements,        # 一行多语句  
            missing-docstring,          # 函数说明，""" """中的内容  
            import-error,               # 找不到的import  
            bad-continuation            # 缩进相关  
    

最终评分为

> Your code has been rated at 9.78/10 (previous run: 9.77/10, +0.02)

  


还有点小得意，去除掉项目风格相关检查后，需要我改的内容不太多呢？

* * *

额外的谈一谈，本周想要展示的内容。

1、上周将第一份工作经历一口气写出来后，我以为我能够继续的一鼓作气将第二份工作也进行一个总结。但在写的过程中，发现那一段经历太过平淡，不知道如何下笔。憋了一千多字之后，先放下。

2、朋友在看过我的第一份工作经历后，对我的内容进行了点评。并推荐给我一本小说：《东莞不相信眼泪》。每天看个十几分钟，还没看完。小说的前半部分提升了我的认知（因为我相信作者所写的内容是真实的）。  


3、现在的我，对第三份工作总结的点评。

4、许多的其他半成品。  


* * *

早上到网吧来发布此篇内容，只有7分钟就要集合，就这样啦~ <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247483721&amp;idx=1&amp;sn=6f8d78eb3c334d5b1796098b8d15e981&amp;chksm=a6c76da491b0e4b29f94f8c2101ac135909e6e4c40a10bf13915e62be74abeb0398ebc927071" rel="noopener noreferrer">原文链接</a>）</small>