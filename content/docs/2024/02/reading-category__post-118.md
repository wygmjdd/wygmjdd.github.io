---
title: 读工具书之《Pro Git》
date: '2024-02-25'
weight: 280680118
primary_category: reading-category
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247486021&idx=1&sn=61c0f3f887827445d3cd39b005e3169f&chksm=a6c766a891b0efbef419a1e70823d6a9db7150b9ca61154237db8d91d7aa94a717f805fed473
---

转眼使用Git已经两年半时间。

刚学会`git add`、`git commit`、`git push`三件套时，整理过[一篇新手期记录](http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484280&idx=2&sn=feb9b4a6cae75a420b03138cc25a34b0&chksm=a6c76f9591b0e6837f9fe7206b1337d1f0b31ad7ff769b9356ac5286dc1cc925f88547612b03&scene=21#wechat_redirect)，现在距离当时已经又过去两年，我对Git的理解更多些了么？

答案是不肯定的。两年来我唯一的进步，只是对`git rebase`的使用更熟练些。

两个月前的一次代码修改中，我需要回退本地已经commit的提交，我记不住应该使用哪个指令。再一次地，我打开手机，在搜索框输入：“git如何回退本地已经提交的commit？”我在那篇已经看过多次的简单博客帮助下带着不确信心态完成这一次回退。

我感受到一丝惭愧，惭愧后便想着完善自己的技能。我完善的方式，是读一本名叫《Pro Git》的书。（读书是我的[一种养成游戏](http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484955&idx=1&sn=b0a6b0619e2cf11e6da321dc462ce0a1&chksm=a6c76af691b0e3e05853d69a9df49105bc6822f00e4357bf8f87961864bc7dd98579f36ff52c&scene=21#wechat_redirect)。）

《Pro Git》是一本完全开源的技术书籍，英文原版地址是`git-scm.com/book/en/v2`，中文版可以在`progit.cn`上阅读。本书的两位作者**Scott Chacon** 和**Ben Straub** 都曾在GitHub工作过。

**Git** ，是一种版本控制工具。

版本控制，在我看来，算是一种日记，日记记录我们每天在某个时刻干了些啥。版本控制呢？则记录我们在某个时刻对代码对资源做了哪些修改。日记可以记在纸质日记本上，也可以记在各种笔记软件中；版本控制信息，可以记录在本地，也可以记录在云端。

管理版本控制信息的工具之一，则是Git。类似Git的工具，还有CVS、Subversion、Perforce、Bazaar等。

《Pro Git》这本书，则主讲Git这个工具，书中主要内容有：Git的起源，Git的安装和环境搭建，Git的基本用法，Git的分支管理，服务器上的Git，分布式Git，GitHub，Git的一些高级用法，自定义Git，Git内部原理等。

读完全书，我的收获主要有以下内容（这算是维护一个记忆目录，待需要时借本篇中记录去帮助回忆具体的使用方式）：

## 一、一些概念性认知

### 1、分支

以前使用Svn时，总是不舍得打分支，我们往往只在做一些较大功能或是每周发布版本时才会打出一个分支。而在本书中，作者是这样说的：Git鼓励在工作流程中频繁地使用分支和合并，哪怕一天之内进行许多次。

Git 的分支，其实本质上仅仅是指向提交对象的可变指针，打一个Git的分支，仅仅是多出一条提交记录而已。

### 2、HEAD

> 那么，Git 又是怎么知道当前在哪一个分支上呢？也很简单，它有一个名为 HEAD 的特殊指针。请注意它和许多其它版本控制系统（如 Subversion 或 CVS）里的 HEAD 概念完全不同。在 Git 中，它是一个指针，指向当前所在的本地分支（译注：将 HEAD 想象为当前分支的别名）。

（关于HEAD，第一遍阅读时仿佛懂了意思，整理笔记时发现又有些模糊。再花一个番茄钟去理解，发现译注是说的很清楚的：HEAD只是当前分支的别名。我猜它的设计功效之一是为了更方便敲指令。）

### 3、子模块

以前网易的客户端和服务端，会共享一个额外的Svn仓库，这仓库中放着一些大家都会使用的共用变量与函数定义。

Git也是可以做到的，做到这功能的关键字是“子模块”。

> 子模块允许你将一个 Git 仓库作为另一个 Git 仓库的子目录。它能让你将另一个仓库克隆到自己的项目中，同时还保持提交的独立。

### 4、Git的实现

Git核心部分是一个简单的键值对数据库。插入任何数据，Git会返回一个键值，通过这个值可以在任意时刻再次检索到这个数据。这些数据都存储在项目的`.git`文件夹下面。
    
    
    # 展示某个SHA-1值所对应的数据，值可以在.git/objects目录下看到，一般是文件夹名称加上里面某一条的文件名  
    git cat-file -p SHA-1-value    
    

对一些大文件的跟踪，Git会打包。
    
    
    # 打包指令，将仓库进行重新打包以节省空间，这指令可以手动调用  
    git gc    
    

### 5、提交准则

1）不要提交空格、tab等空白问题；

2）尝试让每一个提交成为一个逻辑上的独立变更集，即不要一次性提交太多东西；（即便一次改了某个文件许多内容，也可以借助`git add --patch`将这些修改分开提交；）

3）提交信息应该写的完善一些。

### 6、其它

`rebase`是一个很难的操作，看书中的讲解就能感受到其复杂。但有一个原则性的指导：把`rebase`当做是在推送前清理提交使之整洁的工具，并且只在从未推送至共用仓库的提交上执行`rebase`命令，就不会有事。

搭建Git服务器还挺麻烦的，不，其实不算麻烦，而且指令也不算太多。但是呢？我最初接触的是GitLab/GitHub上创建仓库，相较记住许多指令，我更倾向于只需要随意点两下便搞定的使用方式。（作者也如是说，更推荐用方便些的工具。）

各个分支间提交的对比，可以通过`..`、`...`、`^`、`--not`等符号来获取各个提交间的差异。分支间的对比，类似于集合之间的操作：交集、并集、与、或、非。

## 二、使用方法记录

阅读过程中，有一些指令脑子记不住但未来大概率会用到，将其摘抄记录到此处。

### 1、Git三棵树，代码回退

阅读相关章节时，为了更好理解，我借着书中的**三棵树** 画了一张图。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate\(-249.000000, -126.000000\)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)手画的三棵树

下面的指令顺序是回退本地提交的一种方式（本地只有一次提交且并未推送到远端）。
    
    
    # 查看最近两次的修改log  
    git log --oneline -2  
    # 已经提交的log id，此时将本地提交从commit状态变为add状态。此处不能使用--hard，hard会将最新一次提交直接干掉（本指令与git reset --soft HEAD~效果一样，~代表往后回退一个提交）  
    git reset --soft commit_id  
    # 将文件回退到未add状态，此行指令git status会提示（上面一行和当前行，两条指令与git reset --mixed HEAD~效果一致）  
    git restore --staged changefile.c  
    

### 2、许多的指令摘抄，供未来使用
    
    
    # 显示最近两次提交并且展示修改diff  
    git log -p -2  
    # 显示最近一次提交的修改大纲  
    git log --stat -1  
    # 显示最近3次的提交，具体信息只展示作者名字和修改描述  
    git log --pretty=format:"%an %s" -3  
    # 展示短的SHA-1值（log id）  
    git log --abbrev-commit  
    # 显示某个keyword在哪些提交中有做修改  
    git log -Skeyword --oneline  
    # 展示某个提交更改的所有内容  
    git show 1c002d  
    # 展示某次提交更改的所有内容，只显示文件名  
    git show --name-only 1c002d  
      
    # 将文件在Git中删掉，但保留本地文件  
    git rm --cached filename  
    # 追加提交，如果commit漏了内容，可以add漏掉内容执行本指令，将漏提交加到上次commit中去  
    git commit --amend  
    # 列出远程仓库的简写及其对应的URL  
    git remote -v  
    # 标签也可以使用命令行指令打  
    git tag -s v1.5 -m 'my signed 1.5 tag'  
    # 可以为git指令设置别名，git status变成了git st，少敲四个字符，还是挺有用的  
    git config --global alias.st status  
    # 不止单词，长句也可以设置别名  
    git config --global alias.unstage 'reset HEAD --'  
      
    # 打出一个补丁  
    git diff > something.patch  
    # 先试试看这个补丁是否可应用  
    git apply --check something.patch  
    # 将补丁应用到当前项目  
    git apply something.patch  
    # 将diff生成为可以邮寄到列表的mbox格式文件（相较使用diff，作者更推荐此种方式生成patch，因为这种patch中包含了作者信息和提交信息）  
    git format-patch -M origin/master  
    # 配置IMAP或SMTP后，将patch用邮件发出去  
    git send-email *.patch  
    # 应用补丁  
    git am something.patch  
      
    # 选取一条提交到本地分支  
    git cherry-pick commit-id  
    # 快速生成一份包含从上次发布之后项目新增内容的修改日志类文档，一种汇总  
    git shortlog  
    # 查看feature分支上还有哪些提交没有合并到master分支  
    git log master..feature  
    # 清掉那些untracked文件，-n代表的是做这件事前先空跑一下，-d指的是递归处理  
    git clean -d -n  
    # git有自己的grep，从提交历史或工作目录中查找keyword字符串，-n在结果中显示行号，-i忽略大小写  
    git grep -n -i keyword  
    # 查看某文件某几行最近一次是谁改的  
    git blame -L 12,22 filename  
    

### 3、切换仓库用户

某个仓库，我们没有权限，但是拥有权限者的密钥，可以用这样的步骤切换用户。（此处应该还有更好的方式？且先记下可行方法。）
    
    
    # 1. 将秘钥拷贝到相应目录，备份一下自己的秘钥  
    cd .ssh  
    mv id_rsa id_rsa.my  
    mv id_rsa_other id_rsa  
    mv id_rsa.pub id_rsa_my.pub  
    mv id_rsa_other.pub id_rsa.pub  
      
    # 2. test，此时git fetch会报错  
    git fetch  
    # my@url: Permission denied (publickey). fatal: Could not read from remote repository.  
      
    # 3. 切换remote地址  
    git remote -v  # 查看当前远程仓库使用的 Git 保存的简写与其对应的 URL  
    git remote rename origin origin-my  # 此处的origin，是一般的默认值  
    git remote add origin ssh://other@url  # 添加其他人的git链接  
    git config --local branch.cur_branch.remote origin  # 配置当前分支使用的远程仓库名称  
    

### 4、恢复误删除的提交

Git可以借由`git reflog`、`git fsck --full`来恢复误删掉的提交，将它们指向一个新的分支然后重新合并回来。下面是一个简单测试过程：
    
    
    # 回退某个提交，hard将文件搞丢了  
    git reset --hard HEAD~  
    # 查看所有的改变日志  
    git reflog  
    # 查看所有的改变日志，详细版  
    git log -g  
    # 打一个新的分支，f709a2e是刚刚误删掉内容的log id  
    git branch recover-branch f709a2e  
    

丢掉的内容在recover-branch上了。

## 三、小结

《Pro Git》是一本很专业的工具书，书中讲述了Git的许多内容。读完本书，我感觉到自己对Git的使用，是依旧生疏的。想要对Git懂更多些，且继续用下去。

读完本书，我本地的某些测试文件，也将用Git管理（只需要在目录下执行`git init`就可以使用`add`和`commit`啦）。至于是否push到远端，并不重要的，我本地能看到代码或文字的变化过程便好。

  


↓↓↓欢迎关注
