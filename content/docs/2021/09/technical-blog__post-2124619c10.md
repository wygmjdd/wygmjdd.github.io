---
title: Git新手期整理
date: '2021-09-12'
weight: 291764619
primary_category: technical-blog
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484280&idx=2&sn=feb9b4a6cae75a420b03138cc25a34b0&chksm=a6c76f9591b0e6837f9fe7206b1337d1f0b31ad7ff769b9356ac5286dc1cc925f88547612b03
---
我是一个Git新手，从Svn转过来的，这是一篇在项目中使用Git 3个月后，一个新手的记录。

使用Svn期间，听说Git很好用，多次尝试学习并记录了使用记录，但每隔一段时间，这学习的内容都会还给“博主们”。使用3个月后，我相信Git的基础使用，会像游泳、骑自行车一样——即便多年不碰，依然不会忘记（这其实是一个很神奇的事情，得找时间找找看为什么有些技能会一直记得）。这再次验证了学以致用的重要性，许多技能，都是熟能生巧的。

Git有两个基本概念：

  * Git，Version Control System，具体的版本管理操作工具；

  * GitHub/GitLab，代码托管平台，提供远程代码的存储机制。我谷歌了一番它俩的区别，留下的印象是：它们基础功能相差不多，开源项目用GitHub多些，GitLab更多应用于企业内部代码管理。




（网上有一个视频，对Git的基础概念讲的很棒，有兴趣可以看看，末尾附上了视频链接。）

![图片](/images/wechat/2124619c1009/001.png)

来自视频末尾的一张截图

  


Git的大体使用流程是这样的：

  1. 创建Git仓库，可以选用GitHub或者GitLab；

  2. 新建一个Git账号（可以使用账号密码，也可以生成ssh key配对）；

  3. 将远程代码拷贝（git clone url）到本地；

  4. 写代码；

  5. 提交代码（add/commit/push三步走）；

  6. 如果push不上去，需要先处理一番（rebase或者merge，这一步我现在是还有点懵懵的）。




![图片](/images/wechat/2124619c1009/002.png)

Git有一个叫做Graph的功能，可以看到分支的演变

  


这段时间，我使用最多的指令是add/commit/push三连：

  * add，将文件添加到需要提交的列表；

  * commit，将add添加的文件提交一把；

  * push，将代码推到服务器上去。




如果有同事在同一分支先提交了代码，push之前需要先更新，更新过程中可能会有冲突，使用rebase处理，可以让Graph长的有条理一些（是的，现在强迫症点又多了一项——就是想要Graph长的好看些）。

以上，就是我现阶段对Git的全部认识了。

作为从Svn转过来的新手，是一直带着疑惑在使用的。为什么使用Git比Svn麻烦这么多，还被称为比Svn好用呢？大家都说Git比Svn好，真的是这样的么？为什么Git要分两步提交呢？为什么Git提交之前不先检测是否与服务器上有冲突呢？merge是真的不推荐使用的么？Git项目中可以加入公共分支么？

如此多的问题，谨以此文，督促自己，持续学习…… <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247484280&amp;idx=2&amp;sn=feb9b4a6cae75a420b03138cc25a34b0&amp;chksm=a6c76f9591b0e6837f9fe7206b1337d1f0b31ad7ff769b9356ac5286dc1cc925f88547612b03" rel="noopener noreferrer">原文链接</a>）</small>

  


* * *