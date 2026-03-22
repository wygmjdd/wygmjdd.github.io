---
title: 喜新厌旧？有了VS Code，就抛弃Vim？
date: '2022-03-13'
weight: 287820013
primary_category: technical-blog
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484650&idx=2&sn=ecbc1f0e788a0284a31b188cd27d70f4&chksm=a6c7680791b0e111b1f0451f8b33747a3fc3ed55068708f653afa0f17ec78649e12223d225b9
---
工作电脑换成Mac之前，在Windows上面，客户端、服务器代码都用Vim敲，使用起来很是顺手。

换一份工作，电脑换成Mac，感觉MacVim不太好用，又想多看看所用框架是如何实现的，便将写代码的方式改为以下方式：

> iTerm2 + Vim，敲项目代码。
> 
> VS Code，阅读Django源码。

就这样过了9个月。

最近几周，忽然有想法，为什么不用VS Code敲代码呢？我自己配的Vim环境相较VS Code互有优劣，或许我将VS Code配好之后，能够更顺手？

为什么会产生这种想法呢？是因为使用VS Code阅读源码过程中，我发现了一些VS Code比Vim好的地方：

  * 配色。我辛苦配置的Vim配色，没有VS Code默认的好看。

  * 函数（类）定义跳转。Vim，我只借助ctags配置了项目内跳转，VS Code是可以直接跳转到安装的pip包看源码的。

  * 搜索。Vim，使用的rg，碰到前端项目的搜索，会直接将iTerm2卡死；同一个项目，VS Code并不会出现此种情况，速度嗖嗖的。




这想法一发不可收拾，我尝试转变。

经过一周多的摸索，我发现我装在Vim中的插件，VS Code中，竟然都有！！例如：

  * LeaderF，快速检索文件。我记录过[Vim中的配置过程](https://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484063&idx=2&sn=e7138963a0fa96d73042f4d436c99600&chksm=a6c76e7291b0e764a3b0de24a39f13216811aea7052c14cb54d8b8b5ef4819060be0d5348d5f&token=104836683&lang=zh_CN&scene=21#wechat_redirect)，VS Code中，默认为Cmd+P。

  * Easymotion，页面内跳转。VS Code中的Vim插件自带。

  * Flake8，代码检查。Vim中配置的插件为ale；VS Code中插件是Python，它还有很多的选项。




以上配置弄好，敲代码的感受爽了很多。嗯，是发现新大陆的喜悦。

摸索还未完成。

有几个不太影响使用，但能提升效率的，Vim有，VS Code还没找到如何配置的点：

  * 如何能够快速切换文件呢？Vim中使用":b12345"，手不用离开键盘；VS Code使用Ctrl+12345。

  * "."键，有一些情况（比如只输入一个tab），不能重复之前的动作。

  * ":e"操作的目录，不是当前项目的根目录。

  * VS Code的自动补全只能是相关联的变量名？字符串中不支持补全？Vim使用的ycm，只要项目中出现的单词，都能tab出来。




待解决掉上面几个问题，VS Code，将是Vim的全方位增强版！

我决定以后，都用VS Code敲项目代码了……

![图片](/images/wechat/afce8b014c50/001.jpg)

Vim（下）与VS Code的对比 <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247484650&amp;idx=2&amp;sn=ecbc1f0e788a0284a31b188cd27d70f4&amp;chksm=a6c7680791b0e111b1f0451f8b33747a3fc3ed55068708f653afa0f17ec78649e12223d225b9" rel="noopener noreferrer">原文链接</a>）</small>

  


* * *