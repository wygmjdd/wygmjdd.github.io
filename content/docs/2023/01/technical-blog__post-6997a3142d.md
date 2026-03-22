---
title: 分享一个快速、免费搭建个人网站的方法
date: '2023-01-15'
weight: 284746997
primary_category: technical-blog
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247485293&idx=1&sn=e0c28537e625f5f9299c60fabd3a3198&chksm=a6c76b8091b0e296a6e51908f51c1eb2b726fba9b7d97d51d89efba05d9d36cceb6c5e9c7d4d
---
21年，我花258在阿里云买一个服务器，将我的小网站重新部署到互联网。

[当时一番折腾](http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484767&idx=2&sn=148af483e3dfe30f000542728c377e4a&chksm=a6c769b291b0e0a4fce318ec84ca59cc32407e75e2d3aeed3a8e7a632607e0273bd027f687a7&scene=21#wechat_redirect)，将实现纯文本网站的框架从WordPress变成Pelican。WordPress发布新文章，需要在界面上复制粘贴一通操作；Pelican发布文章只需要执行一行指令将Markdown文件转成HTML就好。

当时觉得Pelican比WordPress方便许多，我甚至在GitHub上创建一个项目保留提交记录。由此，我发布一篇新文章的步骤是这样的：

  1. 本地写好Markdown文件，将其放置于正确的目录，提交到GitHub。
  2. ssh连上阿里云服务器，更新最新文章，执行转化指令。



第2步的操作，我感觉是烦的。待新鲜感过去，我便不想再将每周的更新都搬运到自己的小站上。终于，阿里云服务器到期，即便双十一期间每天接到一个阿里云推销电话，我都不再续费。

我的域名又空置了。

最近和飞飞哥（公众号“码农在新加坡”的作者）交流极多，他开始将文章转为视频并取得不错进展（每天能吃一碗小面，还能接到一些公司的工具体验视频邀约）。

和飞飞哥交流过程中，他向我推荐了他搭建网站的方法。由这推荐，我**花两小时将我的小站重新上线** ，这方法**既方便又免费** ，于是有了本篇分享。

我现在发布一篇新文章的步骤是这样的：

  1. 本地写好Markdown文件，提交到GitHub。



是的，我需要做的事情，只是在本地使用我所熟练的工具写好Markdown后，提交到GitHub就好。剩下的事情，都不用管了。

<figure class="figure-with-caption">
<img src="/images/wechat/6997a3142d6f/001.png" alt="图片" loading="lazy" decoding="async" />
<figcaption>修改的内容，都是有邮件通知的</figcaption>
</figure>

具体的搭建步骤如下：

## 一、准备事项

### 1、买一个域名

域名是需要花钱的。但我感觉这钱值得，原因有两点，一是拥有自己的域名是会有一些满足感的，这满足感会成为自信的来源之一。

二是域名也算投资，以前听说“jd.com”是京东花几百万买下来的。京东太大，只以我自己的域名“biyego.com”（当时选这域名有两个意思，一是“毕业狗”，二是“毕业了，go！go！go！冲！冲！冲！”）举例，我花1000元买了10年，前两天上godaddy看，估值已经达到1589刀。

### 2、注册一个GitHub账号

GitHub或是GitLab都可以。（我试过用GitLab，不知道为何拉不了代码，所以推荐用GitHub。）

准备事项到此结束。

## 二、开始搭建个人网站

### 1、创建项目

浏览器打开vercel.com，使用GitHub账号登录。选中一个模板，按照上面的教程，点点点，Vercel会在GitHub上面创建一个项目，这个项目便是网站将要展示的内容。

我选择是portfolio，选择它的原因是它的简介中包含“Markdown”关键字。

### 2、关联域名

域名设置有两个地方需要修改，一是vercel中将项目与域名关联起来，直接按照vercel上面的教程操作就好。（本篇只列举大体框架，并没有很详细的步骤，因为我觉得只要您上vercel点两下，是肯定也能很快搞定的。）

二是上域名服务商，将域名服务器设置为vercel提供的地址。

<figure class="figure-with-caption">
<img src="/images/wechat/6997a3142d6f/002.png" alt="图片" loading="lazy" decoding="async" />
<figcaption>我在godaddy上面的配置是这样的</figcaption>
</figure>

### 3、正式发布

完成以上设置，只需点一下发布按钮，整个网站便部署完成。后面做的事情，只需要将新的页面（Markdown文章）提交到main分支就好。vercel会自动发布的。

以上便是我搭建一个文本网站的步骤。我搜了一下，vercel也是可以有后端的，也就是说，即便想要搭建的网站并非我这样的简单展示，也是可以借助此平台完成的。

更多的使用场景，期待您的发现。 <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247485293&amp;idx=1&amp;sn=e0c28537e625f5f9299c60fabd3a3198&amp;chksm=a6c76b8091b0e296a6e51908f51c1eb2b726fba9b7d97d51d89efba05d9d36cceb6c5e9c7d4d" rel="noopener noreferrer">原文链接</a>）</small>