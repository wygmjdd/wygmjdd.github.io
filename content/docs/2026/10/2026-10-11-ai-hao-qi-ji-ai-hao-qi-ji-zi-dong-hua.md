---
title: AI好奇记｜自动化测试工具e2e
date: '2026-10-11'
weight: 271090006
primary_category: ai-hao-qi-ji
source_url: https://mp.weixin.qq.com/s/AeBz0C5jeqF6Bg38V1uSIg
---
“AI好奇记”在国庆期间停滞一周，停滞原因是为懒惰。所产生的后果，是一种仿佛离开AI行业已经很久的感受。

本周回到工作，所看到的变化有这样几条：

平日使用的GPT Sol模型已经升级到6.1，OpenAI模型版本发布仿佛越来越快。Sol 6.1相较6知识切片晚10天，到26年4月30号。

某百万车型刹车不可靠（最近几天天天看到相关热搜），界系列车再添黑点。

<figure class="figure-with-caption">
<img src="/images/wechat/6b0e868e5792/001.jpg" alt="之前Token用量页面看着清新，现在变得怀旧" loading="lazy" decoding="async" />
<figcaption>之前Token用量页面看着清新，现在变得怀旧</figcaption>
</figure>

CC Switch有一个UI大改版，界面风格显得怀旧，它与Codex有一个相同之处是左侧增添竖栏一条。

## **一、GitHub流行趋势**

这趋势只是本周的。

### **1、https://github.com/boykopovar/AnyPS5**

> Tool for automatic PS5 executables porting to Linux and Windows.

当前星星28.4k，几乎全都是本周增长的，它可做的事情如下：

> 将 PS5 的可执行文件自动移植（Porting）到 Linux 和 Windows 系统上运行。
> 
> 它的核心特点包括：
> 
> 原生格式转换：内置重链接器（relinker），将可执行文件转换为目标系统支持的原生格式。
> 
> 无 emulation 模拟器开销：通过实现适用于动态链接的系统 prx 库，而不是依赖传统的全模拟或独立的运行时进程。
> 
> 着色器重编译：带有着色器重编译工具，可成功生成 SPIR-V 字节码，适用于通过 Vulkan 等技术进行渲染。

这岂不是意味着可以不用买PS5了？

### **2、https://github.com/tester-army/e2e**

> Next generation e2e testing framework for web and mobile apps.

一个自动化测试工具，单看它的介绍我有点没懂如何使用，待让Gemini帮我多解答两次之后，大概懂得了测试流程：语义文本写下测试过程，AI自己去点按钮测功能。

具体的使用方法和对应的实现机制有点长，我已经复制[到此处](https://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247488277&idx=1&sn=0558241e4d273a74004e5ae55326f40d&scene=21#wechat_redirect)。

这个工具不错，改天也得（或者推荐给测试同事）试试看。

## **二、其它**

智能手机拍照时默认上AI，那照片作为证据存在时，是否值得怀疑呢？

现在AI还是不够智能，因为我们的指令还要求“准确表达诉求”，例如：Codex，请告诉我明天重庆的天气。

如果AI的训练数据很多来自于互联网，而互联网上很多的内容来自于AI，AI生产的内容很多都是垃圾，那？

有AI公司开始创造手机了？未来的每台手机，都运行一个独立模型。

> 我同时运行了这么多 cursor 项目（现在有 16 个），以至于我最常用的提示词变成了
> 
> “/bro 从我上次消息开始，把所有事情都给我补上，如果有任何需要我采取行动的项目，就给我足够的背景（执行摘要）来做决定”

这段话很有趣，但我的Cursor Pro年包已在昨天过期。 <small>（<a href="https://mp.weixin.qq.com/s/AeBz0C5jeqF6Bg38V1uSIg" rel="noopener noreferrer">原文链接</a>，更新于2026-10-11。）</small>