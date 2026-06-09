---
title: 好玩的Skill分享之“用马斯克的眼光看问题”，以及一次基于Alma的轻折腾
date: '2026-04-12'
weight: 272910012
primary_category: technical-blog
source_url: https://mp.weixin.qq.com/s/02VDct6cymmqivlMpTHkrw
---
周三分享过一篇“好玩的Skill之‘具体内容’”被删掉，原因大概是某些关键字不能使用，于是重写这分享换成本篇：用马斯克的眼光看问题。

我的开始折腾Skill，来自于偶然看见的一位群友的分享：

<figure class="figure-with-caption">
<img src="/images/wechat/e4efb32d71dc/001.png" alt="图片" loading="lazy" decoding="async" />
<figcaption>截图是新的，来源于GitHub</figcaption>
</figure>

即以某位成功人士的眼光看问题，借助他的思维链式来分析我们普通人所遇到的生活、工作瓶颈，用他们的视野来帮我们找到破局方法。

大概两周以前，我便已经将OpenClaw卸载，而换成新的阿力推荐的Alma，我以为这是一个好用的工具。它替代龙虾之后，也已然替代了我桌面端的ChatGPT。我的试验Skill，现在都于Alma中进行。

这个被推荐的好玩Skill，只用以下指令便将它装上试用成功：
    
    
    npx skills add alchaincyf/elon-musk-skill  
    

安装过程中有弹出它的简要介绍以及触发规则：

> 马斯克的思维操作系统。基于传记、播客、推文、法庭证词、决策记录和外部批评的深度调研，
> 
> 提炼5个核心心智模型、8条决策启发式和完整的表达DNA。
> 
> 用途：作为思维顾问，用马斯克的视角分析问题、审视决策、拆解成本结构、挑战行业假设。
> 
> 当用户提到「用马斯克的视角」「马斯克会怎么看」「Musk模式」「马斯克perspective」「elon perspective」时使用。
> 
> 即使用户只是说「这个成本合理吗」「从第一性原理想想」「白痴指数是多少」「五步算法」「能不能垂直整合」也可触发。
> 
> 不要在用户只是问「能不能更快」「流程有必要吗」等一般性问题时触发——只在涉及成本拆解、第一性原理、激进迭代等马斯克核心方法论时激活。

接着便可以在Alma的窗口问问题：

> 使用马斯克的眼光帮我看看这个网站上的内容应该往哪个方向发展呢？ https://biyego.com/

接下来Alma做的事情，大概是这样几个：

首先通过“马斯克的眼光”“网站”两个关键字命中两个Skill：elon-musk-perspective与web-fetch。

然后使用web-fetch去抓取我的网站内容。

再使用马斯克Skill对我的内容进行分析，得出结论。

我以为这分析很有道理（虽然带些PUA成分且并未抓取全部内容），但我在Chrome中截图不能截全（当然有插件可用呀），于是再给Alma发一条信息：

> 帮我把上面回复的内容，整理为一张清晰直观好看内容不缺失的图片呢？我发现我自己截图不能截取全。

它选中Skill `image-gen`之后，再写一长段Python代码，于机器上装好几个依赖包，生成一个静态网页于浏览器中打开，申请`Screen & System Audio Recoding`权限。

给权限，重启，再发问：

> 你刚刚申请了Screen & System Audio Recoding权限，我给了你权限，然后重启了，现在继续你未完成的工作吧。  
> 截图之前，再审查下你生成的网页呢？我现在看到两个问题：  
> 1、你生成的网页花花绿绿的，我其实更想要简单风格的单纯展示markdown的；  
> 2、我想要的是最初回答中所有内容都能够在图片里面，而不是你的总结

其后再追问几次（问题核心在于它也不能截取完整内容），拿到以下截图：

<figure class="figure-with-caption">
<img src="/images/wechat/e4efb32d71dc/002.png" alt="图片" loading="lazy" decoding="async" />
<figcaption>马斯克告知我的改进方向</figcaption>
</figure>

> 好了，给我整理下整个窗口你做了哪些事情，使用了哪些Skill，并且遇见了哪些问题。将这些整理为一个表格，然后再给我输出一张图片。

<figure class="figure-with-caption">
<img src="/images/wechat/e4efb32d71dc/003.png" alt="图片" loading="lazy" decoding="async" />
<figcaption>输出以上图片都做了哪些事情需要哪些依赖项</figcaption>
</figure>

最后，是这个好玩Skill的汇集链接：

https://github.com/mliu98/awesome-human-distillation?tab=readme-ov-file

最最后，现在的AI，真的已经可以帮着做很多很多事情。

<figure class="figure-with-caption">
<img src="/images/wechat/e4efb32d71dc/004.png" alt="图片" loading="lazy" decoding="async" />
<figcaption>早上这些任务，花MiniMax Coding Plan 201次Token调用 &lt;small&gt;（&lt;a href=&quot;https://mp.weixin.qq.com/s/02VDct6cymmqivlMpTHkrw&quot; rel=&quot;noopener noreferrer&quot;&gt;原文链接&lt;/a&gt;）&lt;/small&gt;</figcaption>
</figure> <small>（<a href="https://mp.weixin.qq.com/s/02VDct6cymmqivlMpTHkrw" rel="noopener noreferrer">原文链接</a>，更新于2026-04-12。）</small>