---
title: 游戏双端程序员转行互联网后端半年，所接触到的新技术们
date: '2021-12-19'
weight: 288660019
primary_category: technical-blog
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484466&idx=2&sn=f2b0c9435a7a9a026c7bc9703dcc4c50&chksm=a6c768df91b0e1c90f81bc7631d5038b98efdb7f842ad45e43609b2441fd07d5c794a4d91815
---
最近刚优化完Django后台界面JSON格式数据的展示，让我感受到一点小小成就感。优化过程中，我特别想写一篇技术博客，说一说整个实现流程；待功能做完，又感觉似乎能说的内容极少——这个优化，是很简单的。（我常有类似感受，一个东西花了很长时间才处理掉，处理完毕之后会觉得如此简单并开始质疑自己如何花了许多时间？）
    
    
    // 有中文的JSON  
    {"insun": "\u6cf0\u56e7 / \u4eba\u5728\u56e7\u90142 / Lost in Thailand "}  
    

JSON数据，包含中文之后看起来乱乱的，会影响我工作效率。我想明白它的具体内容，需要将它的内容复制到一个工具网站上进行查看。我要将这复制粘贴再点一下的过程去掉，我要我所见到的是我能看懂的！

谷歌了一下，似乎做这个优化的程序员并不多，只有一个叫做Django-JSONEditor的自定义控件可用。

按照作者的步骤能够很方便的将问题解决。我因为上面的一个广告按钮而拒绝使用，我以为这广告是Django-JSONEditor加上的，于是自己模仿它的实现做一个自定义控件将其搬到Django中。搬的过程遇见静态资源加载不出来的情况，又一通谷歌，弯弯绕绕的在Django层处理。

待这一步做完，发现广告按钮依然在，才发现是藏在JSON Editor中的物件，将JS文件中的对应代码干掉，便没有广告了。于是知道前端的内容，发布到互联网是会压缩打包的。

本机环境OK后，部署到测试机上，发现静态资源依然不在，这让我接触到Nginx。理解Nginx的（极小部分）使用方式，将它搞定，至此优化结束。

![图片](/images/wechat/f08b707b1879/001.jpg)

GitHub上的效果图  


  


怎么说呢？转行之后，除了主要使用语言（Python）与敲代码的风格（可能可以说是设计模式吧）不变，我是接触到许多新技术的。

  * 苹果电脑与Git，是已经可以熟练使用的基础工具。

  * HTTP协议，感觉已经快有一个大概框架印在心中。以看书的方式了解全局框架之后会是TCP与IP的学习。

  * Docker（容器），认识到它是什么并能进行基础运用。在容器的上层，据说还有管理容器的集群（K8S）。

  * Nginx，是刚接触的。现阶段可以看懂它的基础配置，能够稍微改改，但自己写就还差点意思。

  * HTML与JS，似乎已经藏在几个很复杂的框架后面，要想看到它们，必须先熟悉框架。

  * 许多的我没了解到的内容在等待我去发现。




半年以来，一直在不停地拓展知识广度，我的Python深度之旅，断断续续。谨以此篇说明，我的内功修炼之路，是在前行的。

未来还长，未完待续。

**引用链接** ：

  1. JSON Editor的GitHub地址：https://github.com/json-editor/json-editor

  2. Django-JSONEditor，有人封装的Django版本，按照上面的指引，可以很快用起来：https://github.com/nnseva/django-jsoneditor

  3. 在线JSON转义工具：https://c.runoob.com/front-end/53/

  4. 用一年时间如何能掌握 C++ ？：https://www.zhihu.com/question/23933514/answer/26290066 <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247484466&amp;idx=2&amp;sn=f2b0c9435a7a9a026c7bc9703dcc4c50&amp;chksm=a6c768df91b0e1c90f81bc7631d5038b98efdb7f842ad45e43609b2441fd07d5c794a4d91815" rel="noopener noreferrer">原文链接</a>）</small>

  





* * *