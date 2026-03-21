---
title: 读《图解 TCP/IP》
date: '2022-07-25'
weight: 286480179
primary_category: reading-category
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484974&idx=1&sn=dcb509ed67d23eb6873a3a29539fe384&chksm=a6c76ac391b0e3d566684b6caf57e9b6ae95bdde2bcbbe0c584997ddc82b9b26bec422cbf0ad
---
很多招聘JD（Job Description，工作描述）中，都会有一条“熟悉TCP/IP等网络协议”要求。我换工作到深圳前的某些面试中，也有被问到“对TCP是否了解”，我的回答是模棱的：“我听过它，但没看过实现的源码。”

对TCP是否有了解呢？不了解的。我对它的了解，全都来自于网络博客，遇见一篇，便读一篇。当时能背出些概念，过一会儿便会忘掉。（其中最经典的概念算是“三次握手、四次挥手”，只要被问到TCP，便必然有这概念出现。）

还在网易时，与阿博互相推荐书籍，我向他推荐《[Python源码剖析](http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484104&idx=1&sn=2c24fabdb50675c2a097b11bf4a3e25e&chksm=a6c76e2591b0e733ab143072be20c0d18c9cc5135a27a908e533d7a4cbc88db39aa517e3edb7&scene=21#wechat_redirect)》，他向我推荐《图解 TCP/IP》，当时将它加入待读书单。

真正开始阅读，始于去年10月，到今年5月读完，历时7个月。本书很短，历时很久的原因是，读它的时间，只每周半小时。

本书书名中的“图解”二字，名副其实，书中有许多很形象的图片。贯穿全书的是下图：

![图片](https://mmbiz.qpic.cn/mmbiz_png/aa17lmRY1pWcvYGo4MlLQoakhdSGibX8fLzaiaeWY45nzpY40fkHvia5LkxEpIj9OTxKSRGFCQibh41gPDuYonBViaQ/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)OSI参考模型

书中会借用生活中的场景来阐述各种概念，开篇有一段讲述**协议** 概念的示例，让我欣喜不已，通过这示例，我理解到协议是什么。

> 在此举一个简单的例子。有三个人A、B、C。A只会说汉语、B只会说英语、而C既会说汉语又会说英语。现在A与B要聊天，他们之间该如何沟通呢？若A与C要聊天，又会怎样？这时如果我们：
> 
>   * 将汉语和英语当作“协议”
>   * 将聊天当作“通信”
>   * 将说话的内容当做“数据”
> 

> 
> 接下来，我们分析A与C之间聊天的情况。两人都用汉语这个“协议”就能理解对方所要表达的具体含义了。也就是说A与C为了顺利沟通，采用同一种协议，使得他们之间能够传递所期望的数据（想要说给对方的话）。
> 
> 如此看来，协议如同人们平常说话所用的语言。虽然语言是人类才具有的特性，但计算机与计算机之间通过网络进行通信时，也可以认为是依据类似于人类“语言”实现了相互通信。

接着往后看，更意识到许多网络协议的设计，都来源于生活。

> 计算机通信协议其实并没有我们想象中的那么晦涩难懂，其基本原理和我们的日常生活紧密相连、大同小异的。

比如IP的作用与数据链路的作用：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate\(-249.000000, -126.000000\)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)数据从主机A传输到主机B

> 仔细分析一下机票和火车票，不难发现，每张票只能够在某一限定区间内移动。此处的“区间内”就如同网络上的数据链路。而这个区间内的出发地点和目的地点就如同某一个数据链路的源地址和目标地址等首部信息。整个全程的行程表的作用就相当于网络层。
> 
> 如果我们只有行程表而没有车票，就无法搭乘交通工具到达目的地。反之，如果除了车票其他什么都没有，恐怕也很难到达目的地。因为你不知道该坐什么车，也不知道该在哪里换乘。因此，只有两者兼备，既有某个区间的车票又有整个旅行的行程表，才能保证到达目的地。与之类似，计算机网络中也需要数据链路层和网络层这个分层才能实现向最终目标地址的通信。

我不继续列举书中的各项术语，只说说看读完本书后，我的运用。（不列举原因是本书真的很短，作者讲的真好，直接看原书更好。）

### 1\. 前后端联调

与前端联调，他的电脑连我的电脑，我电脑的IP经常变化，我需要经常将新的IP发送给他。

我们在同一个局域网，想起书中说MAC地址在数据链路层，IP是ARP通过MAC地址找到的。我的MAC地址不会变，那是否意味着前端可以不用每次找我要呢？是不是有工具能够通过MAC地址找到IP地址呢？

是有的，而且是操作系统内置指令：
    
    
    arp -a | grep my_mac_addr  
    

这就是“读完书，留下一个印象，按印象去搜索去解决问题”吧？

### 2\. 抓包

读完本书不久，公司某个域名一直将HTTPS协议转为HTTP协议，为定位该问题，尝试使用Wireshark抓包，捣鼓一番，从协议的流转上，定位到重现流程。（问题只要能够重现，便能解决或者绕过，解决问题的方案，又涉及到更多的知识，更多我不了解、不熟悉的知识。）

那之后，定位另外一个问题，需要看HTTP协议中传输的内容是否准确，再用Wireshark。看到Wireshark中展现的内容，与书中讲述知识一模一样，我是兴奋的。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate\(-249.000000, -126.000000\)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)某次抓包的截图

学以致用的感觉，真好。

《图解 TCP/IP》不错，感谢阿博的推荐。我读完一遍，特将这推荐延续。 <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247484974&amp;idx=1&amp;sn=dcb509ed67d23eb6873a3a29539fe384&amp;chksm=a6c76ac391b0e3d566684b6caf57e9b6ae95bdde2bcbbe0c584997ddc82b9b26bec422cbf0ad" rel="noopener noreferrer">原文链接</a>）</small>

  

* * *