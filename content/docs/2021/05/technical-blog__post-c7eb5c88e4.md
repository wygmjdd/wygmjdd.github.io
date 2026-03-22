---
title: 强力推荐一个vim插件：LeaderF
date: '2021-05-09'
weight: 290900009
primary_category: technical-blog
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484063&idx=2&sn=e7138963a0fa96d73042f4d436c99600&chksm=a6c76e7291b0e764a3b0de24a39f13216811aea7052c14cb54d8b8b5ef4819060be0d5348d5f
---
前两天安利猴哥使用vim敲代码，和他一起搭建vim环境，他收到来自腾讯大佬的建议——用LeaderF进行代码检索。一经使用，便发现LeaderF比我原来所使用的ctrl-p与ctrl-sf，要方便、好用许多，完全满足我开发中的代码查找需求。

快快分享一下。

以下，是我的配置步骤以及使用记录。

## 配置安装

### 初步安装

使用官方文档中的介绍，直接通过bundle安装。
    
    
    Plug 'Yggdroot/LeaderF', { 'do': ':LeaderfInstallCExtension' }  
    

将上述代码加入_vimrc文件，重启vim，敲入BundleInstall安装。

安装完毕，继续编辑_vimrc，将LeaderF文件夹路径放入runtimepath：
    
    
    set runtimepath^=$VIM/vimfiles/bundle/LeaderF  
    

### 额外插件

  * ctags，可以将代码中的所有变量放到一个文件中，类似索引存在。

  * rg，全称为ripgrep，一个类似grep的全文文本搜索工具。




分别在官网上将exe文件下载下来，将存放exe的目录加入环境变量即可。

### 遇见问题-Python支持

完成上述步骤后，打开vim的时候，会出现以下弹框提示：

![图片](/images/wechat/c7eb5c88e4ca/001.png)

通过官方Q&A的引导，知道需要配置pythonthreedll的路径。

我电脑上面安装的是Python39，于是按照如下配置：
    
    
    set pythonthreedll=C:/Users/me/AppData/Local/Programs/Python/Python39/python39.dll  
    

不好使，会报错。

![图片](/images/wechat/c7eb5c88e4ca/002.png)

经过一番折腾（改写斜杠、使用不同的路径、将dll文件复制到vim安装目录）后，新增安装Python36，重新配置路径：  

    
    
    set pythonthreedll=C:/Users/me/AppData/Local/Programs/Python/Python36-32/python36.dll  
    

到此，LeaderF出现在了我的vim中，可以开始使用啦。

![图片](/images/wechat/c7eb5c88e4ca/003.png)

## 使用方式

先试着用一用，在vim命令栏输入
    
    
    :LeaderF xx

得了以下提示：

![图片](/images/wechat/c7eb5c88e4ca/004.png)

由此提示得知，LeaderF是按照分类进行检索的，支持许多种分类，目前使用file、tag与rg。

### 搜索目录下的文件

![图片](/images/wechat/c7eb5c88e4ca/005.png)

这是以前ctrl-p的功能，但是ctrl-p一直以来都存在两个问题：

> 有一系列很相似的文件名，最简单的那个文件名称会筛选不出来，每一次编辑该文件都需要输入绝对路径。
> 
>   
> 
> 
> 根目录与svn挂钩，当当前编辑的文件为根目录下的外链子目录文件，便只能搜索到外链子目录中的文件。（当然，这个问题极有可能是可配置的）  
> 

使用LeaderF后，不再有这两个问题。

LeaderF的file检索，与ctrl-p的操作方式一致。搜索结果，ctrl+j往下移动，ctrl+k往上移动，enter选中文件。

可以设定如下映射，使用快捷键ctrl-p打开按文件名搜索：
    
    
    " 使用ctrl-p打开按文件名搜索  
    let g:Lf_ShortcutF = '<c-p>'  
    

### 通过tag进行搜索

首先切换到对应目录，使用ctags生成一份儿包含全部变量名的文件：
    
    
    ctags --fields=+l -R  
    

之后便可以通过这些变量名快速的找到对应变量的定义位置。

![图片](/images/wechat/c7eb5c88e4ca/006.png)

### 使用rg进行全文搜索  


rg可以按行搜索文件中的具体文本内容。此前在vim中配置了ctrl-sf进行，我嫌弃它慢，就在linux下面用
    
    
    find -name "*.py" | xargs grep "关键字" --color  
    

进行全文搜索。

使用LeaderF的rg搜索，相较linux下面的搜索会慢上一些（第一次速度差不太多，之后的搜索差距还是肉眼可见；不过rg也真的很快了，可接受的），但是会方便许多，因为可以直接在vim下面查找，不用切窗口。特别是，当自己电脑，没有linux环境的时候。

![图片](/images/wechat/c7eb5c88e4ca/007.png)

  


\--

使用过程中，遇见过两个问题：

#### 1\. 关键字搜索，不能展示所有的结果，每次结果都随机出现

LeaderF右下角，会有一个Total:2000000，在bundle/LeaderF文件夹下面使用rg搜索2000000，搜出：

![图片](/images/wechat/c7eb5c88e4ca/008.png)

改一下g:Lf_MaxCount的值后搞定。

猜测原因是：我们项目中的文件太多，总数超过200w行。内部搜索的时候，会随机从200多万中选出200w行进行展示。

#### 2\. 我只想要精确的匹配

见上图中的第3行，2000000匹配到2010 (10.0) is 1600，我并不想这样。

能不能搞掉它呢？我找了好久，找不到啊找不到~

和猴哥持续探讨，忽然，猴哥灵机一闪，告诉我按下ctrl-r可以进行模式切换（Fuzzy与Regex），当切换为Regex不再有上述情况。（到此有一种感触：两个人一起研究新东西，相较一个人，是会事半功倍的）

![图片](/images/wechat/c7eb5c88e4ca/009.png)

当然，还可以修改_vimrc，默认打开即为Regex模式:
    
    
    let g:Lf_DefaultMode = "Regex"  
    

\--

到此，扶正LeaderF，ctrl-sf和ctrl-p被我淘汰掉……

（rg搜索还有个问题——某些中文不能被搜到——暂未找到原因。打算改代码时，如果需要全局修改某个变量，借助另外的工具辅助验证一番）

## 最终的LeaderF配置

配置如下（附注释）：
    
    
    " --------------------------------------------------------------------------------------------------------  
    " LeaderF, 全文搜索  
    set runtimepath^=$VIM/vimfiles/bundle/LeaderF  
    set pythonthreedll=C:/Users/me/AppData/Local/Programs/Python/Python36-32/python36.dll  
      
    " 把搜索的行数搞大一点  
    let g:Lf_MaxCount = 20000000  
      
    " 使用ctrl-p打开按文件名搜索  
    let g:Lf_ShortcutF = '<c-p>'  
    " 使用Ctrl-[打开tag搜索  
    nmap <c-[> :LeaderfTag<CR>  
    " 使用Ctrl-]打开rg搜索  
    nmap <c-]> :Leaderf rg<CR>  
    " 屏蔽掉一些目录、文件  
    let g:Lf_WildIgnore = {  
                \ 'dir': ['.svn','.git','.hg'],  
                \ 'file': ['*.sw?','~$*','*.bak','*.exe','*.o','*.so','*.py[co]']  
                \}  
    " 使用rg搜索的配置项: 不要git/svn/lib文件夹, 不要tags文件，隐藏文件不搜  
    " 不搜索读表目录，瞬间只剩零头  
    " 自动进行大小写匹配，统统搞大点  
    let g:Lf_RgConfig = [  
        \ "--max-columns=0",  
        \ "--glob=!git/*",  
        \ "--glob=!svn/*",  
        \ "--glob=!lib/*",  
        \ "--glob=!info/*",  
        \ "--glob=!tags*",  
        \ "--smart-case",  
        \ "--max-count=200000",  
        \ "--max-filesize=80M",  
    \ ]  
      
    " 窗口自动设定大小，跟着变不甚方便，依然固定大小  
    let g:Lf_AutoResize = 1  
    " 窗口默认为0.5(占比)，习惯小一点，改成0.3.  
    " 有bug啊，只在第1次生效，还是用自动变吧, 当然，是可以直接改掉默认值0.5的  
    " let g:Lf_WindowHeight = 0.3  
      
    " 默认使用正则的匹配  
    let g:Lf_DefaultMode = "Regex"  
    

## 引用链接

  1. LeaderF官方链接，https://github.com/Yggdroot/LeaderF

  2. ctags官网，http://ctags.sourceforge.net

  3. rg官网，https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md

  4. rg的各个选项意义，https://www.mankier.com/1/rg#--max-count

  5. Python支持Q&A，https://github.com/Yggdroot/LeaderF/issues/758 <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247484063&amp;idx=2&amp;sn=e7138963a0fa96d73042f4d436c99600&amp;chksm=a6c76e7291b0e764a3b0de24a39f13216811aea7052c14cb54d8b8b5ef4819060be0d5348d5f" rel="noopener noreferrer">原文链接</a>）</small>




  


* * *