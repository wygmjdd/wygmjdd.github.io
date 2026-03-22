---
title: Cursor初体验
date: '2025-01-31'
weight: 277270006
primary_category: technical-blog
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247486749&idx=1&sn=a6b49e693b5e449161a5320806ef7c38&chksm=a6c761f091b0e8e621a386ba87936c0e061ba16179c1f6279625af78d56a8a6997593e5d68a5
---
某天老板在群里统计大家目前使用的开发工具，我回答说是VS Code，老板再问：“为啥不用Cursor？”

<figure class="figure-with-caption">
<img src="/images/wechat/6d2961b6e207/001.png" alt="图片" loading="lazy" decoding="async" />
<figcaption>阻拦我尝试Cursor的那个报错</figcaption>
</figure>

老板的提问是一个引子，解决掉——其实就只是将Cursor更新到最新——该报错之后，我便开始使用Cursor。两个月过去，我使用Cursor越来越重度，到现在，我想将目前使用Cursor的感受先记一记，于是有此篇。

### 一、初次使用个人感受

可以使用Cursor当天，我并不知道它有什么功能，只在Cursor中（之前是在VS Code中）继续完成我的一个小小测试脚本，我没想到的是，它的tab功能如此强大。如下图，那种仿佛可以预知我想法的代码补全，让我深感诧异。（对的，在我试用Cursor过程中，GitHub的Copilot也已经能免费使用，不过目前我看到的效果是，它在准确性上不及Cursor。）

<figure class="figure-with-caption">
<img src="/images/wechat/6d2961b6e207/002.png" alt="图片" loading="lazy" decoding="async" />
<figcaption>Cursor的tab功能</figcaption>
</figure>

这是一种发现新大陆的惊喜，我甚至开始怀疑，我是不是可以完全抛弃VS Code了。（好吧，这一句有点傻傻的话，是在Cursor中编辑时点按tab出来的，我并没有抛弃VS Code。不抛弃的原因是，同时打开两个应用，一个用来写一个用来看，切换起来方便许多。）

Cursor主要功能分为两种（此处严谨些，或许只是我目前使用到的）：

  * 代码补全，如上图，在编辑过程中，它会依据上下文，自动补全代码；
  * 代码生成，我们可以在某个输入框当中，输入想要做的事情，它会根据输入，再结合整个项目中的上下文生成代码；（关于整个项目，我使用的是Privacy mode，所以还未感受到它的完全体功能：如果上下文更多些，生成出来的代码会更准确。）



需要诚实些的是，我初初使用Cursor时，是真以为它是免费的。但只使用大概5天，免费额度便已经用完。

### 二、薅羊毛

（这个标题，是Cursor帮我生成的。）

薅羊毛的方法，其实也是简单的，免费额度到期后，可以这样操作：

  * 在网站`https://temp-mail.org/en/`上生成一个新的邮箱，使用这新邮箱登录（temp-mail广告挺多，直接在其主页中间框框中收验证码即可）；
  * 再修改下自己机器上Cursor使用的配置文件；

<figure class="figure-with-caption">
<img src="/images/wechat/6d2961b6e207/003.png" alt="图片" loading="lazy" decoding="async" />
<figcaption>一张介绍修改机器的图片</figcaption>
</figure>

修改自己机器上的Cursor配置文件，会有些麻烦，我甚至用Cursor帮我写了一段小小代码：
    
    
    import os  
    import json  
    import uuid  
    import secrets  
      
    def generate_hex_string(length):  
        """生成指定长度的十六进制字符串。"""  
        return secrets.token_hex(length // 2) # token_hex()接受的是字节数，一个字节等于两个十六进制字符  
      
      
    def modify_json_file(file_path):  
        # Change file mode to 666  
        os.chmod(file_path, 0o666)  
      
        # Read the JSON file  
        with open(file_path, 'r') as file:  
            data = json.load(file)  
      
        # Generate two different 64-bit hex numbers  
        hex1 = generate_hex_string(64)  
        hex2 = generate_hex_string(64)  
      
        # Ensure the two hex numbers are different  
        while hex1 == hex2:  
            hex2 = generate_hex_string(64)  
      
        print(hex1)  
        print(hex2)  
      
        # Generate a UUID  
        uuid_str = str(uuid.uuid4())  
      
        # Replace the telemetry fields  
        data['telemetry.macMachineId'] = hex1  
        data['telemetry.machineId'] = hex2  
        data['telemetry.devDeviceId'] = uuid_str  
      
        # Write the modified data back to the JSON file  
        file_path_new = f"{file_path[:-5]}_new.json"  
        os.chmod(file_path_new, 0o666)  
        with open(file_path_new, 'w') as file:  
            json.dump(data, file, indent=4)  
        os.chmod(file_path_new, 0o444)  
      
    if __name__ == '__main__':  
     modify_json_file('./storage.json')  
    

接着，再将替换掉机器码的配置文件替换到Cursor的配置文件中，便可以开始新的体验之旅……

### 三、初次付费

薅羊毛，到底是有些不太方便的，每次过期之后都会点开Cursor的升级页面看一看，我内心想要付费使用的渴望，越来越强……

只是每次都被`每月20刀`吓退。

20刀，用不起，20RMB呢？好像是可以接受的。

我第一次花钱，是在咸鱼花22块钱买一个体验号，商家说可以用一个月，好评再赠送15天。

当我真正用起来后，发现这种体验模式纯纯是骗小白钱，商家帮我做的事情，只是申请一个邮箱而已，体验过期之后，我依然需要换邮箱换机器码。（啊哈，写这一段时，我有些生气，甚至想去找老板退钱……由此，我的建议是，大家如果买号使用的话，**请不要买体验号** 。）

<figure class="figure-with-caption">
<img src="/images/wechat/6d2961b6e207/004.png" alt="图片" loading="lazy" decoding="async" />
<figcaption>Pro账号的界面，长这样子</figcaption>
</figure>

我第二次花钱，是一周之前。我将自己“很想付费使用”的想法在掘金沸点上表达，掘友们给我的建议是：去淘宝买共享号就好。

我上淘宝搜Cursor，找到销量第一那家店，花25块钱买一个月的3人共享号。

目前使用一周，只感觉好香好香！

### 四、使用感受

我现在敲代码，也大概分作两个方向:

  * 项目代码，那些真正会用到我们产品中的内容；
  * 测试与统计工具，测试用作某些技能的预研，统计用于代码上线之后的观察与调整；



项目代码不多说，我只需要写主要逻辑就好，那些log、异常、格式、甚至一些我没有考虑到的逻辑分支，Cursor都帮我完成。

我想要多聊聊的，是测试与统计工具。在写这些测试工具时，我是只用Cursor的代码生成的，即给一段话，让Cursor帮我生成相应功能的代码，这一段话，大概是这样的：

> 帮我写一个函数，这个函数的输入是这样的log文件，它的格式是`timestamp, user_id, action, used time 0.2359 xxxx`这样的，这个函数需要做的事情是根据user_id，统计出这个用户在一天中，使用最多的action，我需要看时间的均值、方差，另外，再帮我生成一个图表。图标具体形式是怎样的我不太懂，但是我需要直观的看出来哪个action使用时间最长，哪个user_id使用最多。

这段话写完之后，Cursor就会帮我生成一个很长的函数。

接下来做的事情，我只需要测试代码是否生成正确，然后，再根据我自己的需求，进行调整就好。

上面过程当然是完美的，当看到那许多数据，都用直观图表展现时，我内心是很满意的。

不完美的地方，有两点：

一是Cursor生成的用作我自己测试的代码，我并不关注它的写法好是不好，我不关注是否可以复用，甚至它内里具体怎样完成我也不关注，这导致的问题是，在我需要对测试做些调整时，我只能再次借助Cursor，而当调整变多时，代码就变得越来越臃肿，更甚者，我会怀疑整段代码得出结论的正确性。

第二个不完美的地方，其实与Cursor无关，而关于我自己知识的储备。以上面一段话作为示例，Cursor帮我生成的图表中，有些很直观，有些我认为还可以做些改进，但其实我，并不知道改进的方向是怎样的，由此，我也并不知道该给予Cursor怎样的提示词。这就是，我有一个万能小助手，却只能让它帮我做些类似洗碗切菜这样的简单事。

Cursor很厉害，但要用好它，我依然需要学习很多。学习，又大概分作两个方向：一是提升自己知识的广度，让自己能够给予Cursor更多相对准确些的提示词；二是提升架构层面的能力，毕竟现在写代码有骨架之后，填肉这件事，让Cursor做就好。

以上，是我使用Cursor两个月所拥有的体验：工具真好用，但自我提升还不能停…… <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247486749&amp;idx=1&amp;sn=a6b49e693b5e449161a5320806ef7c38&amp;chksm=a6c761f091b0e8e621a386ba87936c0e061ba16179c1f6279625af78d56a8a6997593e5d68a5" rel="noopener noreferrer">原文链接</a>）</small>