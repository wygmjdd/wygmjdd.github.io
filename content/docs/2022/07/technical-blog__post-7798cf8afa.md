---
title: 苹果电脑使用心得（2）
date: '2022-07-05'
weight: 286687798
primary_category: technical-blog
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484899&idx=1&sn=5fa38a62a4fa5a2a7c8f57be409b3fa2&chksm=a6c7690e91b0e01862fb6574588de1dde65e8fb0a224245dc272d58c8492040c185b6c635d88
---
使用苹果电脑做开发，已经满一年。相较[之前的整理](http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484368&idx=2&sn=4fe52e9a6a5334eb56a8ae482a82dcfa&chksm=a6c76f3d91b0e62becf714d0cd34e42e48e70b87844a12d5df265fac19579f6fba56dfefe268&scene=21#wechat_redirect)，又多了些设置与工具。

### 1\. iTerm2经常错按快捷键将窗口关掉

使用iTerm2过程中，经常不小心按到[command+w]将窗口关掉，为此搜到一个解决方案。

> To disable [**Command + w**] in Terminal, do the following（按以下步骤禁用）：
> 
>   * From the menu in the top left corner of the screen, select **System Preferences**. Click on **Keyboard** then **Keyboard Shortcuts** then **Application Shortcuts**. （从屏幕左上角的**menu** 菜单，按**System Preferences - > Keyboard -> Application**顺序选择）
>   * Click the + button to add a new shortcut（点[+]号增加一个新的快捷键）
>   * Select "iTerm.app" for the application, and for the command, type Close Window (this is case sensitive). In the shortcut box, give it a different shortcut, like [**Command + Control + w**]（选择“iTerm.app”，“Close Window”，换成其他难按到的快捷键，设置完毕。）
> 


这个办法是将容易按到的快捷键换成不容易按到的。我输入单词“Close Window”、“Close Tab”都不好使，需要使用“Close”。

### 2\. 不使用鼠标进行复制粘贴

某一天在ITerm2中进行分屏操作。我想将右边窗口的目录切换为左边的目录，但不想用鼠标，突发奇想，是不是有办法呢？去搜了一下，两行指令搞定。
    
    
    # 将当前目录复制进剪切板  
    pwd | pbcopy  
      
    # 中间一个快捷键操作将窗口切换  
      
    # cd到新的目录（从剪切板中取出来）  
    cd $(pbpaste)  
    

不过，这种方式有一个不太完美的地方，末尾会多一个换行符，可用下面的指令处理掉。
    
    
    # 我的期望是，将文件名复制到剪切板中  
    # 指令出的结果会在末尾添加一个换行符  
    # 粘贴进Python命令行环境，会直接认为输入完成，报错  
    ls | grep key_word | pbcopy  
      
    # 解决方案是，再多加一条指令，将换行符去掉。完美！！  
    ls | grep key_word | tr -d '\n' | pbcopy  
    

后来我又发现，相较鼠标操作，此种方式还是会慢些。iTerm2的默认配置是**选中即复制，按鼠标中键粘贴** 。

### 3\. 安装postgres之后，不能使用

直接使用指令顺序说明问题。
    
    
    # 安装版本  
    brew install postgresql@9.5  
      
    # 使用指令与报错  
    psql  
    # zsh: command not found: psql  
      
    # 解决方案  
    brew link postgresql@9.5  
    

brew link是做什么的呢？我感觉类似Windows上面的环境变量配置，一个软件可以安装多个版本。

### 4\. 截图软件

最好用的截图软件，我认为是微信。但没有网络的时候呢？

我试过好几个，monosnap、skitch等。最终选择**Snipaste** ，与微信截图一致。

### 5\. ⌘v的使用

iTerm2中敲指令过程，选中某个句子后，直接⌘V则可以将其复制到输入光标后面。

这我是才知道的。以前我的步骤是[选中 -> ⌘c -> 切换到输入光标 -> ⌘v]，省略一个步骤，感觉方便了许多。

如2所说，⌘V可以换成**鼠标中键** ，更加快捷。

### 6\. Clipy

![图片](/images/wechat/7798cf8afaff/001.png)

Clipy的使用

Clipy是一个辅助复制粘贴功能的软件，它能保留历史复制记录，并提供快捷的选择。如上图，当快捷键（我配置SpaceLaucher用Space+2打开Clipy）将Clipy窗口打开后，接着按2，便能将“_”（之前的复制内容）复制到想要的地方。

**Clipy，是我强烈推荐的一个工具！**

这在需要同时复制好几个文本时，特别方便，不用来回切换窗口。

使用过程中，遇见过一个问题，Clipy不能展示图片，各种调整配置均不好使，当时放弃。直到两个月后，看到GitHub上面的发版记录，原来我下载的版本并非最新。使用GitHub上面最新版本后，搞定该问题。

### 7\. 新的博客排版

小飞飞的公众号博文，排版很好看，在请教他之后，我也去找了一下，找到一个我喜欢的工具。

以后与技术挂钩的，都使用此种格式。使用模板见**引用链接7** 。

### 8\. 引用链接：

  1. 修改关闭快捷键的问答：https://apple.stackexchange.com/questions/44412/disable-command-w-in-the-terminal
  2. pbcopy的使用：https://stackoverflow.com/questions/16719970/use-pbcopy-as-path-for-cd-command/27210645
  3. 去掉换行符：https://stackoverflow.com/questions/3482289/easiest-way-to-strip-newline-character-from-input-string-in-pasteboard
  4. Brew link：https://stackoverflow.com/questions/36155219/psql-command-not-found-mac/36156782
  5. Brew link：https://stackoverflow.com/questions/33268389/what-does-brew-link-do
  6. Clipy版本网址：https://github.com/ian4hu/Clipy/releases
  7. 公众号排版：https://editor.mdnice.com/ <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247484899&amp;idx=1&amp;sn=5fa38a62a4fa5a2a7c8f57be409b3fa2&amp;chksm=a6c7690e91b0e01862fb6574588de1dde65e8fb0a224245dc272d58c8492040c185b6c635d88" rel="noopener noreferrer">原文链接</a>）</small>



* * *