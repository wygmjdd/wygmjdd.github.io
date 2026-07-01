---
title: Codex初体验
date: '2026-04-28'
weight: 272750028
primary_category: ji-shu-bo-ke
source_url: https://mp.weixin.qq.com/s/Tc9XIPie8RsAHUzJXJsg2Q
---
如果要说偏爱的话，我想Cursor是我的答案。我的偏爱缘由也可算作简单的，只是这样几个点：

  * 我最初的Vibe Coding工具是为Cursor，有对于工具的习惯性在里面；
  * 我此前为便宜些（月付20刀每月，而年付只需192刀）直接买了一年的Cursor Pro套餐，一年期还不到肯定要持续使用的；
  * Cursor的代码编辑框在UI中占比很重，我依然可以很方便检查它的代码；



但近来的几个转变，又让我生出多多尝试其它工具的想法。

Claude Code（CC）的初使用此前谈过此处不谈，我现在依然极少使用CC，只在需要验证一些Skills效果时用一用它。

此前的那篇《[CC初使用](https://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247487585&idx=1&sn=99f8cf8a4cb4a5546326e7d119c1fb90&scene=21#wechat_redirect)》在小红书的阅读量即将破十万，它将成为我流量最高的帖子。基于此，我总想要试用些新工具，然后记录下即时使用体验去找些流量。Codex作为与CC、Cursor同类型的工具，也是该试试看的。

同时，这样的试用新工具，与10年前折腾不一样的Vim插件类似，都是为更好更快地敲代码。（哈哈，其实也可以这样说，咱内心还是那个愿意折腾工具的新手程序员啦。）

Cursor的新版，已经提醒我好几次它的新迭代：直接于Agents Window下面开发，弱化看代码这一环节，就跟Codex一样。

最近项目组推行使用Codex，公司买了两个Codex大账号（此处我不记得套餐名字，总之是量更大一些）让大家分着用，大家都用而我不用，似乎有些脱节。

于是前两天，我也将Codex装好，配好分发的属于我的api-key用了起来（此处有一个工具叫做CC-Switch，它在配置CC时好用而配置Codex时出bug，我是手动编辑config.toml文件才切换成功的）。

<figure class="figure-with-caption">
<img src="/images/wechat/a7c751702092/001.png" alt="图片" loading="lazy" decoding="async" />
<figcaption>Codex的确认项很多，我的工作变成说“好的”</figcaption>
</figure>

今天是第一次让它实现一个完整功能，下午半天的调研，配上晚上两小时的写代码，再结合前两天的使用，我当前有这样的使用体验：

Codex看代码依赖于其它的IDE（VS Code、Cursor都可以），它弱化看代码这一环节，当需要看代码时会不太方便。

如上图最后一条，UI上面有一个小小bug，它生成待我确认信息后总是会自动收起来文字，我每次都得点开查看，这很不方便。

我现在写代码大体上分作三步走：首先使用superpowers的brainstorming帮我整理需求帮我思考待确认项；代码落地后跑一跑Cursor的Subagent refactor-cleaner优化一版代码；自测通过提交前再跑Command Review，让Cursor基于Review结果再调整一下代码。

这样一套下来，写出来的代码返工率是比较低的。

待切换到Codex之后，并没有方便的/符号唤起指令或是Subagent，只能@插件之后在指令中告知使用brainstorming或者refactor-cleaner（Review也是有指令的），这也算是一点不太方便的地方。

当我记完本篇，Codex写代码也接近尾声，我现在多出一种说不太清楚的感觉，我感觉自己正喜欢着Codex，它的输出它的思考，看起来似乎比Cursor的Auto靠谱些。

说不清楚先不说，且先都用着。 <small>（<a href="https://mp.weixin.qq.com/s/Tc9XIPie8RsAHUzJXJsg2Q" rel="noopener noreferrer">原文链接</a>，更新于2026-04-28。）</small>