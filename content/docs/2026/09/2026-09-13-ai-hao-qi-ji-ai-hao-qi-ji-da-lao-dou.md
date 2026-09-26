---
title: AI好奇记｜大佬都说前沿AI的发展应该减速
date: '2026-09-13'
weight: 271370055
primary_category: ai-hao-qi-ji
source_url: https://mp.weixin.qq.com/s/VRmFrbwJcD2gJ15jMGm2uw
---
谷歌也有Trending，最近一周一直排在前列的，是`iPhone 18 Duo`与`iPhone 18`，苹果新手机的发布，依然话题性十足。那么，折叠屏会是未来的手机发展趋势么？

言归正传，我依然先去翻一翻GitHub。

## **一、GitHub流行趋势**

本周的流行仓库当中，依然有ECC和archify，ECC经久不衰，archify我本周用它在工作中画图一次，画出来的图，依然让我惊艳。

### **1、https://github.com/ayghri/i-have-adhd**

ADHD（注意缺陷多动障碍），是一种神经发展障碍，主要表现为注意力不能持续集中、过度活跃或情绪易冲动等。

> A skill to stop your coding agent from burying the answer. ADHD-friendly output.

i-have-adhd，是本周飙升最快的仓库，如上简介，它依然是一个Skill，它的主要功效，是让coding agent输出的内容可读性更好。

<figure class="figure-with-caption">
<img src="/images/wechat/55abaf75402a/001.jpg" alt="使用它的效果：结果精简了许多" loading="lazy" decoding="async" />
<figcaption>使用它的效果：结果精简了许多</figcaption>
</figure>

### **2、https://github.com/DietrichGebert/ponytail**

> Makes your AI agent think like the laziest senior dev in the room. The best code is the code you never wrote.

只看简介，便觉得这个Skill很有意思。我的已经持续一两年的AI Coding经验中，确实发现AI编程有一个弊端：它经常考虑得特别“全面”，代码写得特别多，还特别喜欢自己造轮子。

这新Skill的做事规矩是：
    
    
    # 1. 需要存在吗？不需要，忽略它  
    1. Does this need to exist?   → no: skip it (YAGNI)  
    # 2. 已经有了？复用，别重写  
    2. Already in this codebase?  → reuse it, don't rewrite  
    # 3. 标准库已经有了？用  
    3. Stdlib does it?            → use it  
    # 4. 平台原生功能可做到？用  
    4. Native platform feature?   → use it  
    # 5. 已经安装的依赖有？用  
    5. Installed dependency?      → use it  
    # 6. 一行代码能搞定？那就一行  
    6. One line?                  → one line  
    # 7. 只有前面都不适用时，才自己实现，而且只做能工作的最小版本  
    7. Only then: the minimum that works  
    

这些规矩很好，我已经将它装在电脑上。

### **3、https://github.com/heygen-com/hyperframes**

> Write HTML. Render video. Built for agents.

我总觉得我这个`AI好奇记`系列真的很不错，只看这些仓库的简单介绍，我就会感到很是好奇。直接渲染视频？现在视频那么火那么难做，写HTML就够了？

<figure class="figure-with-caption">
<img src="/images/wechat/55abaf75402a/002.jpg" alt="什么都不加，只按照example步骤，出了一个对主页的放大缩小视频" loading="lazy" decoding="async" />
<figcaption>什么都不加，只按照example步骤，出了一个对主页的放大缩小视频</figcaption>
</figure>

我按照它官网上的介绍，用Cursor试了一下，发现初版生成效果很是简陋，估计得用心调整才能出可用成品。

但，确实可以出视频的。

### **4、https://github.com/cathrynlavery/diagram-design**

> 38 editorial diagram types for Claude Code, Codex, and Pi. Self-contained HTML + SVG. No shadows. No Mermaid slop.

一个类似archify的画图工具。

### **5、https://github.com/mattpocock/skills**

> Skills for Real Engineers. Straight from my .agents directory.

我阅读文档，记住的第一个用处，类似superpowers的brainstorming，让AI知道我想要的是什么。然后，还有代码重构、bug诊断、测试驱动开发（TDD）等等功能。

这个仓库，来自于一位大佬的真实使用。

<figure class="figure-with-caption">
<img src="/images/wechat/55abaf75402a/003.jpg" alt="大佬的介绍，截图自谷歌主页Gemini" loading="lazy" decoding="async" />
<figcaption>大佬的介绍，截图自谷歌主页Gemini</figcaption>
</figure>

## **二、要点新闻：前沿AI的发展应该减速**

信息来源：

https://darioamodei.com/

https://openai.com/index/an-alien-mind/

本周最大的AI新闻，大概是Anthropic CEO Dario Amodei，以及OpenAI都在呼吁的`让前沿AI发展减速`。

> AI 是“生长”出来的，而不是“设计”出来的——在很大程度上，它是在难以想象的庞大算力上，将一个简单的优化步骤重复执行无数次产出的结果。这造就了一个极其复杂的系统，它通过抽象概念运作，并能模拟人类行为的各个方面。我们可以像神经科学那样，去发现这个系统内部涌现出的各种微观机制的洞察；但与神经科学类似，它的整体行为依然超出了我们能够完全理解的描述范围。

发起这种呼吁的根因，我读完（英文读了一半，更多是Gemini的翻译）上面两篇文章之后，他们发起暂缓呼吁的原因，是自进化的AI当前的发展已经完全超出人类理解，前沿科学家们已经搞不懂AI自进化的过程以及未来会是怎样的。

这呼吁，是一种对未知的恐惧与提前警醒。

> 我们正在面临向一个拥有极高智慧机器的世界过渡的阶段，我们需要确保这一过渡对人类有利。在一个大部分任务都可以由 AI 完成的世界里，我们需要找到维持人类主导权（Human Agency）并恪守“作为人类具有内在价值”的方法；防止在一个原本需要数千名专家、现在只需少数人操作一台大型计算机就能完成事业的世界里出现极度的权力集中；并确保人类始终掌握对未来的控制权，而不至于被超越我们自身、来自“异质心智”的无节制进步所抛弃。

所以问题确实又产生了？未来的AI世界中，真的会产生“无用阶级”么？真的会再次回到集权社会么？（第一次看到“无用阶级”，来源于赫拉利教授的《人类简史三部曲》，它指的是在一个无尽发达的社会，绝大部分人已经不再需要劳动。）

两篇文章当中都提到了可能的解决方案，共同点是加一个“观察员”，对AI做出选择的过程，都做观察与监督。

## **三、一些新出现的名词**

最近的会议当中，经常冒出来我不是很懂的单词缩写，其中在这两周被我记住的，是`FDE`，它的全称是Forward Deployed Engineer，翻译为中文是**前沿部署工程师** 。

对这个岗位的介绍，我去读过两三篇文章，我的理解是：

> 现在很多公司内部的流程、架构或者平台，是可以把AI加入做提效的，但如何加入AI是一个很复杂工作，于是需要一个专有角色来做这件事情，这个角色就是FDE。

--

好啦，本周的整理先到此处。依然耗费近3小时，过程中有感受到心流。 <small>（<a href="https://mp.weixin.qq.com/s/VRmFrbwJcD2gJ15jMGm2uw" rel="noopener noreferrer">原文链接</a>，更新于2026-09-13。）</small>