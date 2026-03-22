---
title: 苹果电脑初使用
date: '2021-10-17'
weight: 289290017
primary_category: technical-blog
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484368&idx=2&sn=4fe52e9a6a5334eb56a8ae482a82dcfa&chksm=a6c76f3d91b0e62becf714d0cd34e42e48e70b87844a12d5df265fac19579f6fba56dfefe268
---
新的工作，换了新的电脑，新的电脑是苹果笔记本。

未使用过苹果系统的我，在新手期，对这电脑，将一些方便自己的配置，做了记录。

### 1\. SpaceLanucher

Windows系统下，有一个好用的功能：Win键+数字，可以很方便地切换任务栏上的应用。养成一种习惯之后，切换到苹果系统下，很是不习惯。一番搜索，找到SpaceLanucher，它与上述功能一致，使用空格键+26键字母，也可以很方便的切换任务。

SpaceLanucher的切换实现，是为应用打开一个新的窗口，如果应用支持多开，那就是多开。

### 2\. 浏览器的F5刷新

没错，苹果系统浏览器的默认刷新键为command+R，但是不符合我的习惯呀。我的习惯是F5。

搜索了一下，在知乎找到答案。

> 系统偏好设置->键盘->快捷键->应用快捷键->点击+号->弹出窗口，应用程序：选择谷歌应用，菜单标题重新加载此页(重点一定要和google app快捷键的标题一样)，快捷键：F5。

上面Chrome的标题是“重新加载此页”，Safari的标题是“重新载入页面”。

设定成功，棒！

### 3\. iTerm2的Tab切换

iTerm2如果打开了多个Tab，会撑满屏幕，依然看着不爽。我找了许久的设定方式：

> Preferences -> Appearance -> Tabs -> Stretch tabs to fill bar.

### 4\. iTerm2与Vim的配色

我用SpaceLauncher不能切换MacVim（只能打开）窗口，所以我改为直接在iTerm2窗口下使用Vim进行编辑。但是颜色我不是很喜欢，就想修改一下。

摸索了一条设置颜色方法。Vim的颜色受iTerm2的颜色配置影响。

网上有一个叫做solarized的工具，可以让iTerm2和Vim的配色保持一致。

在iTerm2下面导入配置，Vim中设定配置，即可统一使用了。具体见图和下面的内容。

![图片](/images/wechat/d22c4677e117/001.png)

选择不同主题  

    
    
    " 1. 从下面地址下载下来配色方案，将solarized.vim拷贝到.vim/colors目录下  
    " git clone git://github.com/altercation/vim-colors-solarized.git  
      
    " 2. vim中的配置选项  
    syntax enable  
    set background=light  
    colorscheme solarized  
    let g:solarized_termcolors=256  
    

不过我最终选择了molokai配色方案，直接满足了我的需求。

修改终端和GUI环境下面的颜色配置，可以在后面链接中查看。

### 5\. cat出来的文件是中文乱码

用下面这一行搞定！
    
    
    cat input.txt| iconv -f GBK -t UTF-8  
    

### 6\. 鼠标悬停在屏幕下方，程序坞会挪位置

如题，3个显示器（是的，3个显示器是极爽的），如果把鼠标悬停到另外两个屏幕（我不想程序坞在这里）下方，程序坞会跑过来。

解决方案很简单：让程序坞悬停在最右边屏幕的最右边（或者最左边）就好。

\--

刚入职时候，是全不熟悉苹果系统的，许多的操作都需要咨询聪聪。使用四个多月后，也只觉得平常，且待我继续探索好用的功能，提升办公效率。

### 引用链接

1、知乎上，浏览器刷新按钮的设定：https://www.zhihu.com/question/29235819

2、iTerm颜色配置：https://github.com/mbadolato/iTerm2-Color-Schemes

3、Vim颜色配置映射关系：https://jonasjacek.github.io/colors/ <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247484368&amp;idx=2&amp;sn=4fe52e9a6a5334eb56a8ae482a82dcfa&amp;chksm=a6c76f3d91b0e62becf714d0cd34e42e48e70b87844a12d5df265fac19579f6fba56dfefe268" rel="noopener noreferrer">原文链接</a>）</small>

  


* * *