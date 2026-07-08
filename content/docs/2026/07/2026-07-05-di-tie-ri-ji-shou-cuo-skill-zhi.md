---
title: “手搓”skill之我终于有了免费的文转图工具
date: '2026-07-05'
weight: 272070005
primary_category: di-tie-ri-ji
source_url: https://mp.weixin.qq.com/s/7iBMuvw38QcHeWeRHaruAQ
---
大概四五年前，当我痴迷于公众号粉丝数增长时，我践行的涨粉方案是四处发帖，将我于公众号上的更新搬运到各个平台：小红书、头条、知乎、虎扑、重庆购物狂……我找到的涨粉博客都在说：“做公众号要去其他平台引流。”

这样的搬运我全手动操作，过程并不顺利，效果也不明显，搬运心思便渐渐淡了许多，只留小红书与知乎继续（知乎此前也已经放弃，直到去年年底重新开始打卡）。

我在小红书的搬运，随着小红书的迭代变化，几年来试过这样几种方式。

首先尝试的是纯文字搬运，小红书图文最多写1000字，超过千字文章的剩余部分我将它放在评论区并置顶。（很长一段时间，我将小红书当做草稿纸使用，只录一些不超过千字的即时输出，这其实是很好的写作练习。）

当某篇文章远超千字时，置顶区域也放不下，我便想着截图。长图太不友好，一张张截又太慢太麻烦，这种方式便自然被放弃。

或许是一年前？小红书新出长文模式，可以将超过千字文章扔进编辑框，它帮着让文字变成图片，这种方式我一直用到一周多以前。

大概是半个月或者更早以前的某个夜晚，我窥见阿力正让AI给他出谋划策，这让我生出新的念头：“为什么不让Cursor基于我的历史输出做些好玩的事情呢？”

我首先做的，是问它“怎么做到坚持更新6年的？”它的回答（[这张图](https://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247487959&idx=1&sn=0bf7cd720476a19bcf10375d35952d64&scene=21#wechat_redirect)）极合理，给予我许多信心。

其后便来到一周前的某天，我脑子中忽然又冒出另一个念头：“为什么不写一个Skill让Cursor来帮我做更多事情呢？比如文生图？反正现在它闲着也是闲着。”（自从[两个月前试用Codex](https://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247487790&idx=1&sn=d3d3399a57b1929ddf71ffbf777b9fd9&scene=21#wechat_redirect)之后，Cursor便已经被我冷落了，甚至Alma以及MiniMax的Coding Plan都几乎不再使用。）

想到，便行动。

上周末阿妮加班，我的绝大部分时间都在新电脑前面度过，除去于公司的干活，剩下的许多心思都关于我的文生图Skill。

构建Skill的过程似乎并不值得复述，依然是基于superpowers的brainstorming表达一个原始念想，让Cursor帮我一步步完善我想要达到的目标；写一版，看看效果，中间用到两个排名前列的UX Skill（frontend-design、design-taste-frontend）；再写再看再改。如此重复而已。

到今天，当它生成效果已经满足我当前审美（生成效果[见这个链接](https://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247487998&idx=1&sn=8838ae21d742cff9a6a92f9a4968392f&scene=21#wechat_redirect)）时，我再生念头：“不然给这个Skill一个独立仓库吧？”

于是有了Skill markdown-to-image的专属仓库：

> https://github.com/wygmjdd/markdown-to-image

欢迎大家试用、提Issue、魔改或者完善（我在新电脑调试Skill，于旧电脑安装使用，所以新机应该很方便使用的）。

它的安装方式如下：
    
    
    # Cursor    
    npx skills add -g https://github.com/wygmjdd/markdown-to-image --skill markdown-to-image -a cursor -y    
    # Codex    
    npx skills add -g https://github.com/wygmjdd/markdown-to-image --skill markdown-to-image -a codex -y    
    # Claude Code    
    npx skills add -g https://github.com/wygmjdd/markdown-to-image --skill markdown-to-image -a claude-code -y  
    

使用方式是直接在Codex、Cursor或者CC的Agent窗口输入如下指令：

> 使用 /markdown-to-image skill帮我把这篇文章转成图片（Cursor使用符号`/`引出Skill，Codex使用符号`$`）：
> 
> @content/docs/2026/05/2026-05-31-30-fen-zhong-ri-ji-15-sui-dai-di-di-shang-po.md

按照提示便可得到结果。

更多详情，烦请移步Readme。 <small>（<a href="https://mp.weixin.qq.com/s/7iBMuvw38QcHeWeRHaruAQ" rel="noopener noreferrer">原文链接</a>，更新于2026-07-05。）</small>