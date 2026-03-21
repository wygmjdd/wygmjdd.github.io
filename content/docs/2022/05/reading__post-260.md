---
title: 为我的小站配HTTPS
date: '2022-05-15'
weight: 287190260
primary_category: reading
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484767&idx=2&sn=148af483e3dfe30f000542728c377e4a&chksm=a6c769b291b0e0a4fce318ec84ca59cc32407e75e2d3aeed3a8e7a632607e0273bd027f687a7
---
最近刚看完《HTTP: The Definitive Guide》，复习读书笔记，想起去年11月因《软技能》驱动，买一个阿里云轻量应用服务器，用WordPress搭建回来的网站——biyego.com。

![图片](https://mmbiz.qpic.cn/mmbiz_png/aa17lmRY1pWAzJ6IJDfknGhoWAMHBfb0IAjqOmy7p3WiawLFTGZjiamw5Y97lSoFHwjLwAmbJMrzejI9KgNjpj4g/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

浏览器地址栏的警告

  


点进去看看，首先映入眼帘的是这个“不安全”标识，它看起来是那么的山寨，于是兴起将它从HTTP换成HTTPS的想法。

搜索几篇博客后，得出大概处理流程：

  * 申请SSL证书。直接在阿里云的“数字证书管理服务->SSL证书->免费证书”中按流程操作一番便可。

  * 将证书下载到本地，再上传到服务器。证书一共两个文件：*.key与 *.pem。

  * 按照阿里云的教程，修改Nginx配置，使得证书生效。




Nginx的配置：
    
    
    #以下属性中，以ssl开头的属性表示与证书配置有关。  
    server {  
        listen 443 ssl;  
        #配置HTTPS的默认访问端口为443。  
        #如果未在此处配置HTTPS的默认访问端口，可能会造成Nginx无法启动。  
        #如果您使用Nginx 1.15.0及以上版本，请使用listen 443 ssl代替listen 443和ssl on。  
        server_name yourdomain; #需要将yourdomain替换成证书绑定的域名。  
        root html;  
        index index.html index.htm;  
        ssl_certificate cert/cert-file-name.pem;  #需要将cert-file-name.pem替换成已上传的证书文件的名称。  
        ssl_certificate_key cert/cert-file-name.key; #需要将cert-file-name.key替换成已上传的证书私钥文件的名称。  
        ssl_session_timeout 5m;  
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE:ECDH:AES:HIGH:!NULL:!aNULL:!MD5:!ADH:!RC4;  
        #表示使用的加密套件的类型。  
        ssl_protocols TLSv1.1 TLSv1.2 TLSv1.3; #表示使用的TLS协议的类型。  
        ssl_prefer_server_ciphers on;  
        location / {  
            root html;  #Web网站程序存放目录。  
            index index.html index.htm;  
        }  
    }  
      
    server {  
        listen 80;  
        server_name yourdomain; #需要将yourdomain替换成证书绑定的域名。  
        rewrite ^(.*)$ https://$host$1; #将所有HTTP请求通过rewrite指令重定向到HTTPS。  
        location / {  
            index index.html index.htm;  
        }  
    }  
    

之前的网站，直接使用WordPress配置，用WordPress控制台编辑文章。WordPress有些卡；写好一遍再重新搬运到其他平台有些烦；编辑完自我介绍，将域名解析到WordPress，网站搭建便算结束。

本周，Nginx配好HTTPS之后，如何将请求转发到WordPress上面，我有些糊里糊涂的。按照搜索到的教程试验一番并不成功。

这过程中，又有想法出现：既然现在已经做互联网后端开发一年，为什么不自己写一个博客平台呢？

接着搜blog framework for programer。看过几篇文章，又出现新的想法——我这网站就只是静态页面而已，先使用pelican就好了？

将云笔记内容搬到公众号，本质上是用Markdown文档生成HTML页面。而这，正是pelican所做的事情。一行指令便能将Markdown文档变成HTML静态页面，如此方便的发布，我为什么不试试看呢？

pelican会在文章末尾加上属于它的标签，我不喜欢这标签，想要再改改。从GitHub上下载下来pelican的源码，将默认主题中的对应内容（contentinfo、extras）干掉，使用以下指令：
    
    
    python setup.py build  
    python setup.py install  
    

重新生成、替代pip的安装，文章的生成，不再有多余标签。总结这篇操作笔记时候，再去看了看官方文档，并不需要如此复杂，按以下指令
    
    
    # 展示主题安装的目录  
    pelican-themes -p  
    

进入到安装目录，将模板改了便会生效。

到整理完想法变迁，又冒出新的想法：作者已经免费让我使用这工具，我为什么要想着将他的标签去掉呢？ <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247484767&amp;idx=2&amp;sn=148af483e3dfe30f000542728c377e4a&amp;chksm=a6c769b291b0e0a4fce318ec84ca59cc32407e75e2d3aeed3a8e7a632607e0273bd027f687a7" rel="noopener noreferrer">原文链接</a>）</small>

  

* * *