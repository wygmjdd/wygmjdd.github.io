---
title: AI好奇记｜大佬都在拥抱AI
date: '2026-10-19'
weight: 271010019
primary_category: ai-hao-qi-ji
source_url: https://mp.weixin.qq.com/s/WPqJGFjnCLPMTXnpljVoEQ
---
最近好几天一直在好奇一个问题：Codex选用模型上的五个档位Light、Medium、High、Extra High和Extra指的是什么呢？Token价格和用量一样么？

<figure class="figure-with-caption">
<img src="/images/wechat/ab5e3cad1151/001.jpg" alt="模型与档位的选择" loading="lazy" decoding="async" />
<figcaption>模型与档位的选择</figcaption>
</figure>

本篇好奇记所做第一件事情，是解答自己的这个疑惑。

<figure class="figure-with-caption">
<img src="/images/wechat/ab5e3cad1151/002.jpg" alt="文档摘抄" loading="lazy" decoding="async" />
<figcaption>文档摘抄</figcaption>
</figure>

我去翻看了OpenAI的文档，得到答案。

这五个档位，设定的是Reasoning effort。

Token价格一致，用量有差异，越高的档位使用的Token也就越多。

显然，新的好奇又出现，什么是`Reasoning effort`呢？

之前的工作中我看到过这个概念，大概类似人类回答问题的严谨程度：随口一说，浅尝辄止抑或深度思考之后给出答案。

我对自己的理解不够确信，再问AI。AI答案如下：

> 它用于动态调节 AI 在回答问题时的“思考深度”与算力消耗。简单来说，就是控制 AI 在给出最终答案之前，允许它在后台“花多少时间、进行多少步逻辑推演与自我检查”。

## **一、GitHub流行趋势**

本周增星超过5k，已经见过的仓库有：AnyPS5、diagram-design（我现在的主力画图工具）、hyperframes，以及大佬的skills。

### **1、https://github.com/morluto/rea**

> Reverse engineer anything with agents, from app behavior down to native binaries.  
> 用 Agent 逆向分析任何东西，从应用行为到底层原生二进制文件。

rea本周增长24w星，一个能够**看懂任意软件实现机制** 的逆向工程整合包，给出证据，甚至直接写出代码。

### **2、https://github.com/storytold/artcraft**

> ArtCraft is an intentional crafting engine for artists, designers, and filmmakers.  
> ArtCraft是一款专为艺术家、设计师和电影制作人打造的、有意图的创作引擎。

看起来像是以前的3D编辑器中添加了AI功能，未尝试。

### **3、https://github.com/NationalSecurityAgency/ghidra**

> Ghidra is a software reverse engineering (SRE) framework  
> 一个逆向工程框架。

> Ghidra 是由美国国家安全局（NSA）开源的一个软件逆向工程（SRE）分析框架，支持对多种处理器架构和平台的编译后代码进行反汇编、反编译、图形化分析及扩展脚本开发。

与上面的rea有一些差异。

#### **1\. REA 是什么？（AI 的“眼睛”和“工具箱”）**

  * **本质** ：它本身**不是** 一个独立的逆向分析引擎，而是一个**胶水层（MCP Server + CLI）** 。
  * **作用** ：它把各种现有的逆向、分析工具（如底层的 **Ghidra、Hopper、IDA** ，以及处理 JS/Electron、Web、固件、APK 的工具）统一封装成标准接口。
  * **核心价值** ：它让 AI Agent 能够**自主调用** 这些工具去“看”代码、跑分析、查日志，并在得出结论时**连同证据链一起交出来** （比如指出某项逻辑对应的是哪个二进制偏移量或代码块）。



#### **2\. Ghidra 是什么？（底层的“显微镜”和“重工业引擎”）**

  * **本质** ：是一个功能极其强大、由美国国家安全局（NSA）开发的**独立软件逆向工程（SRE）分析框架** 。
  * **作用** ：提供完整的主界面（GUI）或无头模式（Headless），专注于对各种处理器架构的编译后二进制文件进行**深度反汇编、反编译、图形化流图分析和脚本化扩展** 。
  * **核心价值** ：它是人类安全分析师或逆向工程师用来手动或者通过编写自定义脚本（Java/Python）死磕底层二进制的**核心重型武器** 。



#### **3\. 核心差异总结**

**维度**| **Ghidra (` NationalSecurityAgency/ghidra`)**| **REA (` morluto/rea`)**  
---|---|---  
**角色定位**| **底层引擎 / 独立逆向工具** （重工业级）| **Agent 插件 / MCP 调度层** （AI 胶水层）  
**使用者**| **人类逆向工程师 / 安全研究员**| **AI Coding Agent** （如 Claude Code 等）  
**交互方式**|  复杂的用户图形界面（GUI）、独立应用或命令行批处理| 通过 MCP 协议由 AI 自动发起调用、返回带有证据链的结构化结论  
**覆盖范围**|  专注于编译后的原生二进制文件（多架构汇编与反编译）| **万物皆可逆** ：不仅能调 Ghidra/Hopper 看二进制，还能管 JS/Web 运行时、Electron、APK、抓包等  
  
**简单来说** ：**REA 往往会把 Ghidra（或者 Hopper、IDA 等）作为它底层的“武器”之一调动起来** 。REA 负责指挥 AI 去自动化完成逆向任务，而 Ghidra 则是被AI（或人类）用来真正深度剖析二进制代码的专业引擎。

## **二、大佬言论**

最近一周，我已经看见好多位大佬说他们正拥抱着AI，且愿意将更多时间花在更有意思事情上来。

以下内容摘自Tim Sweeney（Epic Games founder and CEO）。

### **1、原文**

When I was writing Unreal Engine 1, my time was divided as follows:

  * Around 30% went to seriously deep coding on hard problems: assembly language texture mappers, C++ BSP trees, data persistence, object oriented systems design, and networking.

  * Around 70% was just typing and refactoring large bodies of code needed for a complete engine feature set. This was not hard, and while I was doing it my mind was mostly on the deeper coding topics, thinking and planning for what's next. It didn't feel much different from vibe coding today, except that it was just me typing code on an IBM Model M keyboard rather than prompting it and reviewing the results.




So, it has always seemed perfectly logical that we would rely on AI for that 70%, once the AI could do it with a similar quality standard as we could, which has never been perfection. It came as no surprise that, after a few years of AI model evolution, it was able to take the reigns on that 70% and free up programmers' time for more valuable tasks.

What's more of a surprise is the emergence of AI as a sort of insta-Carmack able to solve hard technical problems quite cleverly and often cleanly, and that it's able to reason about and work in complex 3D scenes both by operating the tools and by directly understanding the raw data files.

I abandoned assembly language in 1998 when out-of-order CPUs made much simpler C/C++ code faster, and never I missed it. If prompting through architectural documents, concept art, and design plans can transcend typing code and tweaking vertices, that will enable developers to spend their time on higher-level, higher value technical and creative tasks.

What matters is the end product, whether it's a game or an engine. Anything developers can do to try out more ideas and make better software and games faster is a win for everyone.

### **2、译文**

我在编写 Unreal Engine 1 时，时间分配大致如下：

  * 大约 30% 的时间用于真正深入地解决复杂的技术问题：汇编语言纹理映射器、C++ BSP 树、数据持久化、面向对象系统设计，以及网络通信。
  * 另外 70% 的时间，只是在编写和重构大量代码，以实现一套完整的引擎功能。这些工作并不困难，而且在做这些事情时，我的思绪大部分都放在那些更深层次的编码问题上，思考和规划接下来要做什么。这与今天的氛围编程（Vibe Coding）并没有太大区别，只不过当时是我自己在 IBM Model M 键盘上敲代码，而不是通过提示词让 AI 生成代码，再对生成结果进行审查。



所以，在我看来，一旦 AI 能够以与我们相近的质量标准完成那 70% 的工作，让 AI 来承担这些工作就是一件再合理不过的事情。毕竟，我们自己写代码也从来做不到完美。经过几年的 AI 模型迭代，当 AI 能够接手这 70% 的工作，将程序员的时间释放出来，让他们去做更有价值的事情时，我对此并不感到意外。

更令人意外的是，AI 开始展现出某种「即时版卡马克」的能力：它能够相当巧妙、而且往往很干净利落地解决棘手的技术问题；它还能够对复杂的 3D 场景进行推理和操作，既可以通过操作工具来完成工作，也可以直接理解原始数据文件。

1998 年，当乱序执行 CPU 的出现让简单得多的 C/C++ 代码跑得比汇编语言更快时，我就放弃了汇编语言，而且此后从未怀念过它。如果通过提示词，结合架构文档、概念艺术和设计方案，就能够超越手动敲代码、调整顶点的工作方式，那么开发者就能把时间花在更高层次、更有价值的技术和创意工作上。

真正重要的是最终产品，无论它是一款游戏，还是一套引擎。开发者能够做任何事情，只要这些事情可以帮助他们尝试更多想法，以更快的速度打造出更好的软件和游戏，那对所有人来说都是一件好事。 <small>（<a href="https://mp.weixin.qq.com/s/WPqJGFjnCLPMTXnpljVoEQ" rel="noopener noreferrer">原文链接</a>，更新于2026-10-19。）</small>