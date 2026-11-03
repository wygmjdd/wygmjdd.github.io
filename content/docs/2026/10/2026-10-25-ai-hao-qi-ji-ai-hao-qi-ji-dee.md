---
title: AI好奇记｜DeepSeek Harness试用、新工具以及为Cursor再花钱
date: '2026-10-25'
weight: 270950025
primary_category: ai-hao-qi-ji
source_url: https://mp.weixin.qq.com/s/Sih0me79eOLKEVI5pLFHhQ
---
周一更新CC Switch时，看见它的下方新增`MiniMax Code`，想要试试国产产品，便将它下载下来。

<figure class="figure-with-caption">
<img src="/images/wechat/d2021fe229c3/001.jpg" alt="CC Switch页面" loading="lazy" decoding="async" />
<figcaption>CC Switch页面</figcaption>
</figure>

很久以前我还听说`DeepSeek Harness`，也将它同时下载下来。

随便点两下后，我只保留下来DeepSeek Harness，原因很简单：MiniMax Code不能用MiniMax的Coding Plan，而DeepSeek Harness可以。（我是卸载之后才回想起来CC Switch是专门做切换Token源这件事的……）

<figure class="figure-with-caption">
<img src="/images/wechat/d2021fe229c3/002.jpg" alt="DeepSeek Harness试用" loading="lazy" decoding="async" />
<figcaption>DeepSeek Harness试用</figcaption>
</figure>

Cursor已经过期，未来一段时间自己项目的浅用，有了替代品。

周六，我使用MiniMax M3、GPT 6.1 Sol、Grok 4.5 Fast、ChatGPT Classic（模型为6，但不知道具体是哪个）读取我所记录的身体变化表格截图，其中就MiniMax读错图片，且乱说，这让我对MiniMax的信心降低许多。

## **一、GitHub流行趋势**

本周增星超过5k但已经见过的仓库有：

  * https://github.com/cloudflare/security-audit-skill，一个让编码 AI 代理通过多阶段、沙箱隔离和独立验证来自动执行代码库安全审计并生成机器可读漏洞报告的工具。

  * https://github.com/stablyai/orca，一个专为 100x 开发者打造的 AI 智能体编排器与工作台，支持让 Claude Code、Codex、Grok 等任意 CLI 智能体在各自独立的 Git 工作树中并行运行，并在一个统一的界面中进行管理。

  * https://github.com/heygen-com/hyperframes，一个开源的 HTML 转视频渲染框架，允许用户通过 HTML、CSS 和可寻址动画（如 GSAP）直接编写并生成确定性的 MP4 视频。




### **1、https://github.com/anomalyco/opencode**

> The open source coding agent.

OpenCode我已经听过多次，却一直没有真正使用过。它是一个开源的Coding Agent，与Claude Code、Codex、Cursor属于同一类工具。

Claude Code与Anthropic的模型生态结合得更紧密，Codex则更适配OpenAI的模型，OpenCode支持接入多种模型。因此，它将Agent框架与底层模型相对解耦，让开发者可以自由选择模型，并通过同一套工具体验不同模型的编程能力。

### **2、https://github.com/Graphify-Labs/graphify**

> Turn any codebase, with its docs, SQL schemas, configs, and PDFs, into a queryable knowledge graph. A /graphify skill for Claude Code, Cursor, Codex, and Gemini CLI: local deterministic AST parsing, every edge explained, no vector store.

译文：

> 将任意代码库，包括其中的文档、SQL Schema、配置文件和 PDF，转换成一个可以查询的知识图谱。
> 
> Graphify 是一个面向 Claude Code、Cursor、Codex 和 Gemini CLI 的 Skill。它通过本地、确定性的 AST 解析来构建知识图谱，每一条关系都有据可查，而且不需要向量数据库。

看起来像是另一个替代RAG的工具哎，不对，看过它的介绍之后，它是一个本地代码阅读器，用以辅助Codex（当然也包含其他的类似工具）更好地阅读代码。

阅读介绍时，我生出三个疑问，并让Gemini做了解答，Gemini的解答内容太长，我将它挪到[一篇可声明AI创作的文章](https://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247488363&idx=1&sn=0206bf2dfdc2019fb73e643da7161db8&scene=21#wechat_redirect)中去。

我最终的结论，是`Graphify`好用，但暂时先不替换我已经在使用的`CodeGraph`。

## **二、其它**

### **1、埃隆·马斯克说**

🚨 埃隆·马斯克警告：人类最多只有3年时间，对于那些拥有技能或创造力从中获利的人来说……之后，游戏规则将永远改变！

“过去200年的模式（我给你薪水，以换取你的时间和努力）即将接近终点……人工智能将吞噬绝大多数常规工作，支付报酬换取工时将彻底失去意义！”

在这个转变背后，隐现着现代人类历史上最大规模的财富再分配地震。那些洞悉游戏规则的人正在悄然行动，而那些等到它成为“突发新闻”再行动的人，将连一张桌子上的座位都找不到！

即将到来的游戏规则极其严苛且务实： 归根结底，重要的不是你工作多少……而是你拥有什么？

如今最聪明的赌注，不是把钱冻结在传统房地产里，也不是追逐数字货币……而是构建一个完全由AI驱动、让你睡觉时也能倍增的数字收入系统：

🎯 目标受众 + 数字产品 + 智能分发渠道 = 永不停歇的生产机器（$10k/月）。

时间飞逝……要么今天就构建你的智能资产，要么成为那个被时代吞噬、喝干的老旧经济的一部分！⚡️🔥

--

我在《人类简史三部曲》中其实已经见过这个问题：当绝大部分人类都成为了“无用阶级”，那时的世界将会怎样呢？

实话说，我不知道。

但我相信，会有许多类似罗辑的存在去关注整个人类命运的。

### **2、关于花钱**

今晚问Grok问题，它不答，得升级，既然决定[不买腾讯体育会员](https://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247488339&idx=1&sn=dddea2e35f02b36ceafda54f61b0cf81&scene=21#wechat_redirect)，而MiniMax M3不太靠谱，便花80刀开了一年X的最便宜会员，它能低额使用Cursor、Grok。 <small>（<a href="https://mp.weixin.qq.com/s/Sih0me79eOLKEVI5pLFHhQ" rel="noopener noreferrer">原文链接</a>，更新于2026-10-25。）</small>