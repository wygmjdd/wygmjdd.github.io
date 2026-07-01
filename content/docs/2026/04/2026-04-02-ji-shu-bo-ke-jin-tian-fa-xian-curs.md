---
title: 今天发现Cursor的refactor-cleaner很好用
date: '2026-04-02'
weight: 273010006
primary_category: ji-shu-bo-ke
source_url: https://mp.weixin.qq.com/s/nTy-xkw-hhU2jgGPLIna_A
---
那大概也是十年前的事情了，当时萌哥还是我的导师，他向我推荐了《重构》。

这本书我大概读了一半（又似乎读到三分之二），总之该是没有读完的。

具体的代码重构规则我并不能很好记住，比如函数的短小，带数据的实体变成类之类。

我所记住的，只是这样两个原则：

首先有自动化测试工具，改代码前后的输入输出，需要有个小帮手帮着确定。

其次是重构过程中的每个改动应该尽可能的小，改一下代码，跑一下小帮手。这样的节奏下去，不至于让重构后的代码面目全非。

那之后的工作中，可算作是有将这些原则应用到工作中的。我们都对自己代码的整洁很有洁癖，我们会互相讨论将代码如何写得更好看，我们每隔一段时间，就对自己系统的代码做做全组汇报——code review。

自从此前[试用Claude Code](https://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247487585&idx=1&sn=99f8cf8a4cb4a5546326e7d119c1fb90&scene=21#wechat_redirect)帖子小小火了一把（可能会是我的第一篇10w+阅读帖子）之后，我有特意去关注Cursor（对的，我现在的主力工具依然是Cursor）的那些Plugins、Skills、Agents。

最近又开始一个新项目的初期搭建，今天晚上提交一波代码后有再改一点代码，此时的我发现Cursor（我模型绝大多数情况下都使用的Auto）写的代码太不注重美观（主要是函数太长，重复代码略多，Rules并不能约束住），我便想起“重构”。

以前代码的不美观，我都指出不美观处让Cursor再改。但前面两周Cursor的更新，它已经不再让我决定是否accept而全部帮我accept了……

我的对代码的审查，门槛变高很大一截(因为代码已经写入本地，Cursor改写的内容，只能通过Git Diff查看。每多一个步骤，我检查代码的动力便少上一分。)

今晚代码风格不美观的再发现，我想起“重构”的同时，也想到“是否已经有Skill或者工具”来帮我做这件事情呢？

<figure class="figure-with-caption">
<img src="/images/wechat/06b3a9040ce8/001.png" alt="图片" loading="lazy" decoding="async" />
<figcaption>refactor-cleaner</figcaption>
</figure>

我在对话窗口输出“refa”，还真让我看到了名叫“refactor-cleaner”的一个subagent，它的介绍简单些说是：清理僵尸代码、去掉重复逻辑。

<figure class="figure-with-caption">
<img src="/images/wechat/06b3a9040ce8/002.jpg" alt="图片" loading="lazy" decoding="async" />
<figcaption>running refactor-cleaner</figcaption>
</figure>

眼前一亮的我对我的小改动（大概一百行左右吧）执行了此subagent。它重构的结果，是让我很是满意的：重复代码被提取出来，函数短了许多。

晚上下班地铁上，觉得此发现值得做一次小小记录，于是作此记录。 <small>（<a href="https://mp.weixin.qq.com/s/nTy-xkw-hhU2jgGPLIna_A" rel="noopener noreferrer">原文链接</a>，更新于2026-04-02。）</small>