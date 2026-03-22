---
title: 一个后端工程师初学前端
date: '2023-01-29'
weight: 284600029
primary_category: technical-blog
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247485309&idx=1&sn=7867fd064c1e01e072cf3b56052bfa40&chksm=a6c76b9091b0e28638fc8bd1664d0a4e755f9fa3a55bd8811db4b5641289953a8a896bdf58dd
---
前段时间发现一个前端的bug：上传文件需要校验MD5，前端每次上传文件的MD5是不变的。

鉴于最近正在学习如何做前端开发，我自己也去搜搜原因可能出在何处。待确认原因并生成正确MD5后，跟前端小哥的结果一对，发现我的想法是正确的。感觉自己似乎已经知道前端在做什么了，于是起笔总结一下最近一段时间（日期跨度是1个月，有时间时便学一学，攒下来的总时长，大概20多个小时）的学习成果。

这总结，大概分为三个部分：茫茫不知所措、复制粘贴复制粘贴、似乎懂点什么了。且按照这步骤，来记录一下我的学习经历吧。

### 一、茫茫不知所措

我最初设计后端接口时，会经常想省流量（以前做游戏的习惯）将Dict换成List传递，这被好几位前端小哥抵触，于是便反思自己，我是不是不了解Web开发的规则啊？Web开发不需要考虑数据量大小的？

按照《[HTTP: The Definitive Guide](http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247485023&idx=1&sn=6c755166648d4b0ce98ace6f5f9f07ba&chksm=a6c76ab291b0e3a431cacd168eca2f68d30ae647c408e67302f6aa6901ef21123ed9e2f1a57c&scene=21#wechat_redirect)》书中所说，应该是需要考虑的，不然不会用缓存、拥塞控制等存在。我的猜测是，对比页面中随随便便一张图的大小，来自于数据格式改变的省流，是微不足道的。传Dict，开发效率是会高一些的。（这一点在很多书中都有体现，不能只顾着效率而不考虑代码可读性。）

最近的一个小项目，正好有机会让我学习一下前端开发。该项目的功能只是在页面填入某几个字段，点一个按钮后向数据库中导入许多数据。

从哪里开始呢？我之前经常听到的名词有React、Vue、NodeJS、npm、Yarn、JQuery……

我先按照React的入门教程抄出来一个井字棋。抄完之后，发现依然不知道怎么开始做我想做的事情，但好歹知道React是什么了：React是一个类似Django的开发框架。

再搜搜看，得知Vue跟React是相似的东西，React做偏大型项目，而Vue做一些小东西。

正好前端小哥有一个小项目是用Vue开发的，我便开始照着抄。抄之前，先用以下指令新建了一个项目：
    
    
    # 1. 创建项目，统统选了默认值  
    npm init vue@latest  
      
    # 2. 按提示启动项目，启动成功后在浏览器上输入提示链接就好  
    cd vue-project  
    npm install  
    npm run dev  
    

### 二、复制粘贴复制粘贴

我选取一个页面，照着搬过来，发现事情并不像想象的那样顺利。接着将与这个页面相关的内容统统粘贴过来，依然不行。

原来Vue跟Python一样，如果需要用到某些功能，需要安装一些指定的库。
    
    
    # 1. Python安装md5库  
    pip install md5hash  
      
    # 2. Vue安装一个md5库  
    npm install blueimp-md5  
    

等到将所有用到的内容都安装上，一个所改即所得的页面出现在我的面前。接着在后端写了一个接口，用自己写的前端代码去调用这个接口。调用成功的时刻，我感觉自己仿佛变成了一个全栈工程师。

### 三、似乎懂点什么了

复制粘贴的过程中，我发现Vue项目有这么些规律：

  1. main.js是整个项目的入口点。
  2. JavaScript与其它语言一样，需要用的函数、控件，都需要导入才能使用。
  3. *.Vue文件有3个部分：模板、样式和脚本。模板负责网站页面有什么内容，样式觉得这些内容长什么样子，脚本负责这些内容的交互。
  4. 要让Vue页面能够展示，需要把它配置到router表里面。



我在原有界面中添加一个按钮，点击按钮选择文件，再打印出文件的MD5。好了，有了重现步骤，便定位到问题出在每次参与计算MD5的值并非文件内容，而只是文件对象。

我这么厉害，这么快定位到问题，让我起了写下本篇博客的心思。想着博客代码好看点，便想着新建一个页面来展示我对前端开发的理解，我新建出来的Vue文件是这样的:
    
    
    <template>  
        <div>  
            <AButton @click="uploadFile">  
                <UploadOutlined />  
                上传附件  
            </AButton>  
            <input ref="uploadRef" type="file" accept=".xlsx,.docx,.pdf,.png,.zip" style="display: none"  
                @change="beforeUpload" />  
        </div>  
      
    </template>  
      
      
    <script setup lang="ts">  
      
    import { ref } from 'vue';  
    import { UploadOutlined } from '@ant-design/icons-vue';  
    import md5 from 'blueimp-md5';  
    import MD5 from "crypto-js/md5";  
      
    const uploadRef = ref();  
      
    function uploadFile() {  
        console.log('----------------> uploadFile', uploadRef.value)  
        uploadRef.value.click();  
    }  
      
      
    function beforeUpload() {  
        const file = uploadRef.value?.files[0];  
        console.log(file)  
        console.log('md5:', md5(file));  
        console.log('MD5:', MD5(file).toString());  
      
        var reader = new FileReader();  
      
        reader.onload = function (e) {  
            const contents = e.target.result;  
            console.log('md5 contents:', md5(contents));  
            console.log('MD5 contents:', MD5(contents).toString());  
        };  
      
        reader.readAsText(file);  
    }  
      
    </script>  
      
    <style scoped lang="scss">  
      
    </style>  
    

将按钮展示出来后，点击按钮时，报了以下错误：
    
    
    runtime-core.esm-bundler.js:218 Uncaught TypeError: Cannot read properties of undefined (reading 'click')  
        at uploadFile (BeforeInsert.vue:29:21)  
        at callWithErrorHandling (runtime-core.esm-bundler.js:155:22)  
        at callWithAsyncErrorHandling (runtime-core.esm-bundler.js:164:21)  
        at emit$1 (runtime-core.esm-bundler.js:718:9)  
        at runtime-core.esm-bundler.js:7410:53  
        at handleClick2 (button.js:102:7)  
        at callWithErrorHandling (runtime-core.esm-bundler.js:155:22)  
        at callWithAsyncErrorHandling (runtime-core.esm-bundler.js:164:21)  
        at HTMLButtonElement.invoker (runtime-dom.esm-bundler.js:339:9)  
    

好吧，这卡住了我总结的流程，卡了很久，为什么呢？为什么呢？

放在另一个页面中就ok，为什么新建一个就不行了呢？搜一搜ref的定义，我猜测可能是我这个界面没有挂载到某个“root”上面，那如何挂载呢？

改改改改改改改，乱乱乱乱乱乱乱乱乱改……

竟让我发现这报错不在这个页面，与另一个页面中的一个AModal组件关联起来。如果加了AModal，就报错，不加，就不报错。为什么会这样子呢？

且先看看茫茫多的“Vue warn”是啥。
    
    
    [Vue warn]: Unhandled error during execution of watcher callback  
    

请教前端小哥哥，他说他从来没有碰到过，搜索的结果，也对不上。我肯定碰到了一个很小的错误……

我自己断断续续来回尝试过好多次，终于是没搞定的。

回到办公室（之前在家办公自己琢磨），再次请教了前端小哥哥，前端小哥哥打断点追进Vue源码，发现问题出在Vue版本上面。待我将Vue版本从3.2.41改到3.2.43后，该问题不再。

本篇整理，便到此处吧，如何打断点，如何追源码，且后面再说。反正我已经可以调用后端接口，可以看文件的MD5，可以开始我的前端开发了。

### 4\. 引用链接

学习过程中用到的一些网站：

  1. React的入门教程：https://zh-hans.reactjs.org/tutorial/tutorial.html
  2. 查看JavaScript语言的API：https://developer.mozilla.org/zh-CN/docs/Web/API/File
  3. 查看可使用的组件：https://antdv.com/components/select
  4. 我碰见的bug：https://github.com/vuejs/core/issues/7070 <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247485309&amp;idx=1&amp;sn=7867fd064c1e01e072cf3b56052bfa40&amp;chksm=a6c76b9091b0e28638fc8bd1664d0a4e755f9fa3a55bd8811db4b5641289953a8a896bdf58dd" rel="noopener noreferrer">原文链接</a>）</small>