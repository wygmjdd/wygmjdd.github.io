---
title: 使用VS Code一年，捣鼓笔记
date: '2023-04-04'
weight: 1150704702
primary_category: technical-blog
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247485478&idx=1&sn=1eeba13b452bf483ade4ab7b97e94f9c&chksm=a6c764cb91b0eddd3221fd5b939a03dac0f2ae7414da72973435574d8b85645ee7201078a9b0
---
去年将敲代码IDE[从原生Vim切换到VS Code](http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484650&idx=2&sn=ecbc1f0e788a0284a31b188cd27d70f4&chksm=a6c7680791b0e111b1f0451f8b33747a3fc3ed55068708f653afa0f17ec78649e12223d225b9&scene=21#wechat_redirect)之后，会时不时捣鼓一下这新的开发工具。

以下是我在捣鼓过程中记录的一些在脑子中记不住的内容。

### 1、快速跳转项目内的代码错误

使用Vim时，我配置使用`Ctrl+m`和`Ctrl+n`来回跳转代码中由`flake8`检测出来的语法报错或是不符合规范写法的提醒。

VS Code有没有呢？有的，以下是默认配置：

> Keyboard Shortcut: ⇧⌘M （打开本项目中的所有错误）
> 
> Quickly jump to errors and warnings in the project. （在窗口中选择错误快速跳转）
> 
> Cycle through errors with F8 or ⇧F8.（可以使用F8和shift+F8来回切换）

### 2\. 连按不成功

有时候，VS Code中连按按键e，会弹出一个小框，并不能连续的往后跳单词。

弹出的小框是“元音音标提示框”，只需要使用以下指令将其关闭就好。
    
    
    defaults write NSGlobalDomain ApplePressAndHoldEnabled -bool false  
    

### 3\. Terminal窗口与编辑窗口间的快速切换

使用VS Code敲代码一段时间后，已经习惯所有的编辑都在VS Code中做。

但偶尔需要写一些简单测试代码时是需要打开iTerm2并回归Vim的，想到是否可以直接在VS Code中编辑，再在VS Code中执行测试代码呢？

是可以的，右键选择`Run Python File in Terminal`即可。

编辑窗口和Terminal窗口的切换，只能用鼠标，让我感觉很是不方便。

搜啊搜……

在Stack Overflow上找到答案，我将步骤从Stack Overflow上搬运下来。

  1. 用`Ctrl+shift+p`（Mac上面是`Cmd+shift+p`)打开指令选择窗口。
  2. 搜索到"Preferences: Open Keyboard Shortcuts File"后回车。
  3. 添加下面的配置：


    
    
    // Toggle between terminal and editor focus  
    {  
        "key":     "ctrl+`",  
        "command": "workbench.action.terminal.focus"  
    },  
    {  
        "key":     "ctrl+`",  
        "command": "workbench.action.focusActiveEditorGroup",  
        "when":    "terminalFocus"  
    }  
    

按上面步骤配置后，使用`Ctrl+删除`可以快速在两个窗口间切换。

继续浏览上面帖子，发现使用`Cmd+j`是可以快速开关Terminal窗口的。

### 4\. 从iTerm 2中直接打开VS Code

在VS Code中使用`Cmd+p`，搜索`> Shell Command: install 'code' command in Path`，点击一下。

接着打开iTerm2，cd到想要使用VS Code打开的目录，使用以下指令：
    
    
    code .  
    

便在VS Code中打开当前文件夹了。

### 5\. copy on select （选中复制）

在VS Code中的Terminal里面选中即复制。

使用`cmd+,`打开设置窗口，搜索`copyOnSelection`，选中即可。

### 6\. 使左边的Activity Bar占用空间变小

公司的显示器是2K屏，将代码全按照`PEP 8`标准写之后，可以将敲代码窗口分成4屏：左右两边的竖格用来看代码，中间两个竖格用来改代码，方便许多。

每一个格子不够宽，于是将最左边的`Activity Bar`藏起来。刚刚好。

这导致使用`Explorer`、`Extensions`等功能很不方便。（快捷键太多也会记不住的。）

于是找到插件`Activitus Bar`用起来，作者开发这插件的初衷是：

> One of my work colleagues was complaining about the activity bar wasting too much space……（Activity Bar占了太多空间。）

这插件将`Activity Bar`中的按钮都挪到下方的`Status Bar`上，占据空间变小许多。

可以按照插件介绍直接在`settings.json`配置文件中修改图标。

PS：`Activity Bar`的名称可以在哪里找，还请大家指教呀……

### 7\. 引用链接

1、查看代码错误的官方文档：https://code.visualstudio.com/docs/getstarted/tips-and-tricks

2、长连按的配置说明：https://zihengcat.github.io/2018/08/02/simple-ways-to-set-macos-consecutive-input/

3、`Editor`与`Terminal`快速切换配置：https://stackoverflow.com/questions/42796887/switch-focus-between-editor-and-integrated-terminal

4、`Activitus Bar`的介绍：https://marketplace.visualstudio.com/items?itemName=Gruntfuggly.activitusbar

5、VS Code支持的图标集：https://microsoft.github.io/vscode-codicons/dist/codicon.html

6、找`Activity Bar`名称的提问：https://stackoverflow.com/questions/75927538/where-to-find-vs-code-activity-bars-name

<figure class="figure-with-caption">
<img src="/images/wechat/866754702adf/001.png" alt="图片" loading="lazy" decoding="async" />
<figcaption>超高的代码屏占比（14寸屏幕）</figcaption>
</figure>

为追求更快更稳更方便的敲代码体验，持续捣鼓中…… <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247485478&amp;idx=1&amp;sn=1eeba13b452bf483ade4ab7b97e94f9c&amp;chksm=a6c764cb91b0eddd3221fd5b939a03dac0f2ae7414da72973435574d8b85645ee7201078a9b0" rel="noopener noreferrer">原文链接</a>）</small>