---
title: '读《HTTP: The Definitive Guide》（一）'
date: '2022-08-15'
weight: 286270177
primary_category: reading-category
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247485023&idx=1&sn=6c755166648d4b0ce98ace6f5f9f07ba&chksm=a6c76ab291b0e3a431cacd168eca2f68d30ae647c408e67302f6aa6901ef21123ed9e2f1a57c
---

去年刚转行到互联网时，所做事情是在旧有系统中做些迭代，依样画葫芦。对Web开发的整体框架，是不了解的，彼时甚至觉得“前端”、“后端”两个词，怪怪的（游戏开发中的说法是“客户端”、“服务端”）。

为了能够对自己改的代码有更多的认识，我搜寻关于Web开发的建议，其中有一条是“熟悉HTTP（Hypertext Transfer Protocol）”。其时我已经有了“学东西要从书中系统学习”的认知，并养成[小步伐](http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484955&idx=1&sn=b0a6b0619e2cf11e6da321dc462ce0a1&chksm=a6c76af691b0e3e05853d69a9df49105bc6822f00e4357bf8f87961864bc7dd98579f36ff52c&scene=21#wechat_redirect)习惯，于是找到《HTTP: The Definitive Guide》。

刚开始阅读本书时，我在笔记中做了以下记录：

> 转行第一步，先将HTTP相关内容搞熟悉。
> 
> 目前（2021年07月21日）看起来，一天看2页的话，一共596页。岂不是需要300天看完？也就是说周末或者平时，如果有时间的话，必须得加速看了。一天10分钟不太够用的。

阅读本书的时间，是午饭后午休前的十几二十分钟，至2022年5月9日读完，历时10个月。

周末，我是没有看本书的；较计划提前些的原因是，中午的10分钟，不止10分钟（此处请允许我再提一次——抗衡拖延症的诀窍是——告诉自己“马上开始看书，只看10分钟”；当然，反过来似乎也成立：“再刷10分钟小红书，绝对是最后10分钟了”）。

读完之后，有把HTTP搞熟悉么？将此问题抛一边，且先看看本书的主要内容。

本书一共分为6个部分：

>   * Part I describes the core technology of HTTP, the foundation of the Web, in four chapters.
>   * Part II highlights the HTTP server, proxy, cache, gateway, and robot applications that are the architectural building blocks of web systems. (Web browsers are another building block, of course, but browsers already were covered thoroughly in Part I of the book.) Part II contains the following six chapters.
>   * Part III presents a suite of techniques and technologies to track identity, enforce security, and control access to content. It contains the following four chapters.
>   * Part IV focuses on the bodies of HTTP messages (which contain the actual web content) and on the web standards that describe and manipulate content stored in the message bodies. Part IV contains three chapters.
>   * Part V discusses the technology for publishing and disseminating web content. It contains four chapters.
>   * Part VI contains helpful reference appendixes and tutorials in related technologies.
> 


为提升阅读英文文档的能力，本书我阅读的是英文原版，故有以上摘抄。

这种持续性的英文阅读，我有感受到英文阅读能力的微弱提升——对不太艰难的概念，我能连贯阅读下去并保留前面一段的记忆，我开始能顺着作者的思路思考。读本书之前，是可能会读了这句忘记上句的，注意力，绝大部分在翻译上面。

我将上面一段，按照我的理解将其简单翻译如下：

>   * 第一部分分4个章节讲解HTTP核心技术与Web基础。
>   * 第二部分分6个章节讲解构建Web系统所需要的各样组件：HTTP服务器，代理，缓存、网关、机器人（爬虫）。浏览器也是Web系统框架的一部分，之前已经讲过，本部分不再赘述。
>   * 第三部分分4个章节介绍了跟踪标识、安全性、内容访问控制等技术（大概像是回房间拿东西，需要正确的钥匙）。
>   * 第四部分分3个章节，讲解HTTP消息主体、操控和描述消息主体的相关标准。
>   * 第五部分分4个章节，讲述发布与Web内容的传播。
>   * 第六部分是有用的引用与相关技术的教程。
> 


整理这篇读书总结时，去看了书籍大纲与阅读过程中的读书笔记，有一种自信想法浮现：“如果用现在的认知去重新看一遍，我想书中的许多内容我都知道说的是什么了。”或许我读本书的时机，有些过早？应该在有一定基础，能将书中内容与实际运用进行结合之后再看？

读完本书，我熟悉HTTP了么？我觉得我没有，写下本篇时，书中绝大部分内容，我都已经忘记。

但似乎又确实多了些记忆，在学新知识的某些时刻，在敲代码的某些时刻，在某些需要解决问题的时刻，在尝试阅读Django源码的时刻……

都似曾相识。

为此，我在咸鱼上花29元买了本书的实体中文版置于办公桌上，打算碰到依稀概念时，翻一翻。

  


* * *

  
↓↓↓欢迎关注
