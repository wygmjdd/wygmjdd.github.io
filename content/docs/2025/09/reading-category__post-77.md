---
title: 《编码》说：“二维码也是一种编码”
date: '2025-09-07'
weight: 275080077
primary_category: reading-category
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247487145&idx=1&sn=c4d692dd14230e08cc81c73ce59238f7&chksm=a6c7624491b0eb524e043fa509ae9da2ef7596deae3e3b9b16f4506673e3c4350b377c3c425f
---
最近收到一本新书，它的名字叫做《编码：隐匿在计算机软硬件背后的语言（原书第二版）》。

过去10天，它一直不离开我视线。

![图片](https://mmbiz.qpic.cn/mmbiz_jpg/aa17lmRY1pUsIiakAzAxjjp2F7dtBkgB4ib7koswLibdtd8uGlY6xgZk8IcpiaOoAbsrgyPY6CImCaCtt0FpMSC9Ug/640?wx_fmt=jpeg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)《编码：隐匿在计算机软硬件背后的语言》

正如两年前花25小时[读完《编码》第一版后的读书笔记](https://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247485553&idx=1&sn=75c433e6aa343169ba0f759e9cd57543&scene=21#wechat_redirect)所写：“这是一本小书，读来很耗时间，但真的有帮助我理清楚一台计算机是如何被搭建起来的。虽然全书由浅入深，再到最深处理解起来很难，但我依然很推荐，跟着书中步骤，再给自己足够时间，真的可以搭建出来一台完整的计算机。”

《编码》第一版出版于1999年9月，我在23年初次阅读时，丝毫没有感受到它的“陈旧”：计算机的基础构建规则，即便时隔二十多年，变化依然不大。

电路理论是基础，二进制计数体系对应着“灯泡”的开和关，许多的开关按照一定逻辑组装在一起则出现逻辑门与加法器，再多一点，则出现内存、处理器；开机之后电脑如何运作，是为操作系统。

《编码》第二版的中译本初版于25年8月上市，收到新书后的前面几天，我一页一页往后翻，在相熟处跳过，在晦涩处逗留，我看到书中内容，在内核不变基础上，有多出许多新内容。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate\(-249.000000, -126.000000\)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)会动的时钟

建造一个时钟，靠着振荡器、触发器的连接，控制一秒、十秒、一小时、十二小时、二十四小时。使用辉光管、数码管显示具体的十进制数字。

（此处要诚实一点，当读书进度过半，书中许多内容我都已经做不到精细复述，我啊，只是新维护一个目录：如果要做一个数字时钟，可以翻阅《编码》第二版第18章。）

算数逻辑单元（ALU），是CPU最基础的部分，它是负责加减运算及其他基本运算的核心部件。

寄存器在ALU处理字节时存储这些字节；数据总线是所有输入和输出之间的互连，它是一条所有组件输入和输出共用的数据通路。

链路中的值如何“上”总线，以及如何“下”总线，是新增的CPU控制信号章节。

跳转、循环和调用，重复即是循环，计算机所做的工作，绝大部分都是重复的；跳转是循环的实现机制，做完一件事，跳到起点再做一遍；调用依赖于堆栈（我以为翻译在此处只使用“栈”应该更好理解一些？）。

《世界大脑》是一本虚拟的百科全书，它呈现“对现实的通用诠释”和“对思想的统一”，我们对知识的积攒已经很多，我们靠着互联网找到、共享这许多知识。互联网，是电脑与电脑之间的联系。

新的内容，除开以上章节之外，还有章节中内容的更新，它们是近20年来流行的事物。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate\(-249.000000, -126.000000\)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)本书的ISBN号

比如二维码是怎样构造出来的。

二维码已经是生活中随处可见的标志，但其实我，从没有想过它是怎样构建的。在《编码》第一版当中，作者说明二进制数在真实世界中的使用时，举例只有UPC码（也叫条形码，或者一维码）。UPC码黑色为1，空白为0，最终转变成一个个代表食材、商品的数字。

二维码和UPC码一样，也是一种编码的表现形式，它也黑色为1白色为0，只是在这规则之外，又多出许多规则，比如三个位于角上的大方块是定位图案，比如接近右下角的较小方块是对齐图案，比如靠近顶部和左侧的横向和纵向黑白交替的方块序列被称为定时图案，以及包围整个二维码的白色边框是为静默区。

最后，随着新书出版的，还有本书对应的配套网站：https://www.codehiddenlanguage.com。网站上的内容，是书中内容的补充。

是的，网站上的时钟真的会“动”。

翻完《编码》第二版，我想自己书架，又多出一本很值得收藏的实体纸质书——感兴趣时便再翻一翻。 <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247487145&amp;idx=1&amp;sn=c4d692dd14230e08cc81c73ce59238f7&amp;chksm=a6c7624491b0eb524e043fa509ae9da2ef7596deae3e3b9b16f4506673e3c4350b377c3c425f" rel="noopener noreferrer">原文链接</a>）</small>