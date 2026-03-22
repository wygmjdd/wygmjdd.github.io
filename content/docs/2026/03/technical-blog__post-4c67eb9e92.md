---
title: 初次尝试Claude Code，以及所感受到的与Cursor间的差异
date: '2026-03-07'
weight: 273270004
primary_category: technical-blog
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247487585&idx=1&sn=99f8cf8a4cb4a5546326e7d119c1fb90&chksm=a6c77c8c91b0f59acee0770c7853c924789caee62876954ebbc6433a90126d56e07b2c2b94aa
---
使用cursor已经快一年半，对后来才流行的Claude Code（后面简称cc）一直不尝试。最近公司内发起Vibe Coding风，我在这风中受同桌影响也试用了cc。

我的尝试方法，与同桌一样：花261买一年的MiniMax Coding Plan，将cc里面的默认模型按照MiniMax官网文档改为MiniMax（对的，有官方文档，还有一个很方便的工具叫cc switch，可更方便的切换模型）。

今天的初次尝试cc，大概分作两个方向：一是将它当做code review工具，二是真正用它敲代码。

code review也使用了两种方式，一是它默认的指令/review，我们仓库并不放在GitHub上面，当它检查PR不到时会默认回退为检查本地diff，它确实是能够看出来问题的。另一方式是插件市场安装的code-review插件。

目前两个review我都使用的不深，但从它的输出来看，和GitHub上面的默认用Gemini review效果差不太多。我还有一个想象是，是不是可以直接给它们commit id让它们做事情呢？

我用cc敲代码，首先感受到的与cursor的最大差异，是它的指令都只在一个输入框输入，看来似乎是压根不需要打开编辑器进行代码编辑的。

之前在网易，受萌哥的影响，我有大概五六年时间都仅仅使用原生Vim写代码。我以为cc所给我的第二印象，是它的diff真好看呀，仿佛回到当年一样。（后来编辑器换成VS Code，再换成cursor。）

最后是它代码的生成质量，当我使用plan模式，让它将plan做好几次改动之后再写出的代码，是符合我之前设置代码风格的。我再让cursor检查它的代码，其中的可优化项并不多，只找到一处错误。

总之，我的初次尝试cc，给我一种新鲜感，又给我一个不确定是短期还是长期的编码方式：未来，就让cc和cursor互相协作吧，一个写代码，另一个做code review工作。 <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247487585&amp;idx=1&amp;sn=99f8cf8a4cb4a5546326e7d119c1fb90&amp;chksm=a6c77c8c91b0f59acee0770c7853c924789caee62876954ebbc6433a90126d56e07b2c2b94aa" rel="noopener noreferrer">原文链接</a>）</small>