---
title: 初次尝试git worktree——让cursor帮我同时干两份活
date: '2026-04-16'
weight: 272870007
primary_category: ji-shu-bo-ke
source_url: https://mp.weixin.qq.com/s/-Pdi1uc8mOgMINd-v8_rOw
---
依然来自于阿力的发现，他在两周前的某天向我展示了他忙时的工作模式：“我现在开了四个cc窗口，每一个都在分别干活。

“它们属于同一个仓库，只是分属于不同分支。

“启动很简单，只需要使用git的worktree就行，然后每个文件夹下面都是独立分支。”

在阿力的分享之后，我有去简单搜了下git worktree是什么（我此前有看过[一本专门讲解Git的书叫做Pro Git](https://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247486021&idx=1&sn=61c0f3f887827445d3cd39b005e3169f&scene=21#wechat_redirect)，对worktree却一点印象都没有，是有些神奇的。我去书中确认了下，有worktree概念，但没介绍过此种用法），然后有了这样的理解：

我此前的开发，都在同一个分支上进行，当需要在另一个分支做些改动时，采取的步骤是这样的：
    
    
    git stash  
    git checkout target-br  
    git commit  
    git push  
    git checkout ori-br  
    git stash pop  
    

如果改动并不很大，过程中我还会添加git rebase来将改动同步到ori-br。总之是，一番操作下来，到最后的git stash pop时，是需要处理些冲突的。如果于另一个分支上的改动很耗时，我可能还会忘记此前的改动都有些啥。

而git worktree的存在，便是为了解决这个问题。worktree所做的事情，其实是在本地直接新建一个文件夹，这个文件夹下面会直接新建一个分支（我今天是新建的分支，我理解直接checkout到某个已存在分支肯定也是可以的），如果需要在新分支改些问题，直接切换到新分支目录下去做改动就好的。

最近工作很有些忙，今天下午我忽然回忆起阿力的操作。简单请教下阿力，再基于他的分享开始让cursor帮我试做这件事。

我原有的分支，依然做正需要做的事情A。新建的分支，去做另一个可算作较底层的与A无关的langfuse集成完善。cursor依然很牛，两个agent各做各的互不干扰。

但过程中的我却感受到两处不便利。

首先是确认的容易搞错。cursor每个agent做完事情后我都需要确认（这是我现在的工作模式，我让它做每件事之前都让我看过方案待我确认后再执行），当切来切去好几遍之后，我有一次将新的指令输在错误的窗口导致上下文被污染。

然后是merge代码时的失误。git merge这条指令，也需要先做git stash。agent1 merge代码前，首先执行了git stash，而agent2此时正在修改代码，agent2的修改被搞坏后再自我修复。到agent1 merge完之后再做git stash pop时，有了冲突。这冲突cursor额外花好几分钟处理。

以上，是我今日初次尝试worktree的记录，它可算是有好有坏。

好的地方，是我确实让cursor同时帮我做了两件事。坏的地方，是我的确认竟然成了它并行开发的瓶颈！

是否可做些改进呢？

问题一，慢一点是可以避免的。

问题二，可以不着急merge代码，可在许多工作都完成之后再做这件事。

未来是否还会继续用呢？

或许会吧？但前提，一定得是我知道自己在做什么，且大概知道怎么做。

因为啥都不会？那出来的东西，大概率将是shit！ <small>（<a href="https://mp.weixin.qq.com/s/-Pdi1uc8mOgMINd-v8_rOw" rel="noopener noreferrer">原文链接</a>，更新于2026-04-16。）</small>