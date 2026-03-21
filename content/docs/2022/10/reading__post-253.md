---
title: '读《HTTP: The Definitive Guide》（二），初看RFC'
date: '2022-10-10'
weight: 285710253
primary_category: reading
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247485136&idx=1&sn=0045722fe8002f870bffce6b3d19405b&chksm=a6c76a3d91b0e32bae7c069255c8d923f9cb211e3ec1145be47465ae3eea3064bc99433e9712
---
某天，与前端就一个图片展示问题做讨论，他想要浏览器中输入的图片链接能够直接展示图片于浏览器上，而并非自动下载。

怎样能够做到呢？

简单搜索一番，得知只要将Response Header中的Content-Type设定为“image/png”即可。（png可换成jpeg等其它子类型。）

设定Content-Type之后，并未生效，图片依然被下载下来。

经过另一位前端小哥提点，得知原因在于Content-Disposition：
    
    
    content-type: image/webp  
    content-disposition: attachment; filename="colorhub.webp"  
    

将Content-Dispostion中的attachment替换为inline后，实现了该效果——Chrome打开新标签页，输入图片地址，图片被展示出来。

待我改完之后，发现前端想要的效果是在页面中展示图片，并非新开标签页查看。

他是可以用以下形式做到的：
    
    
    <img class="card-img-top photo-preview" src="//cdn.colorhub.me/9z-fWrEX26w/rs:auto:0:500:0/g:ce/fn:colorhub/bG9jYWw6Ly8vNjAvMDIvMmJlZmFkNjMwOWQ3ZTdkZTMwYTI0YWYzODMyYTQzYzhiZDEzNjAwMi5qcGVn.webp" alt="食物，甜点，蛋糕" title="食物，甜点，蛋糕" style="width:auto;">  
    

img标签中，只需要指定src即可，与Conetent-Disposition无关。

这新知识的获得，让我感觉到自己对Web开发的许多细节，是很不熟悉的。

不了解它，便尝试了解它。为了解Content-Disposition的作用，于是有了本篇。

### 1\. Content-Disposition是什么？

#### 1.1 基础定义

定义来源于RFC 6266：

> The Content-Disposition response header field is used to convey additional information about how to process the response payload, and also can be used to attach additional metadata, such as the filename to use when saving the response payload locally.

Content-Disposition返回头的目的是指定如何处理返回信息，也可以用来附加其它的元数据，比如保存内容时指定文件名称。

#### 1.2 语法解析

整个Header的语法如下：
    
    
    1.     content-disposition = "Content-Disposition" ":"  
    2.                            disposition-type *( ";" disposition-parm )  
      
    3.     disposition-type    = "inline" | "attachment" | disp-ext-type  
    4.                         ; case-insensitive  
    5.     disp-ext-type       = token  
      
    6.     disposition-parm    = filename-parm | disp-ext-parm  
      
    7.     filename-parm       = "filename" "=" value  
    8.                         | "filename*" "=" ext-value  
      
    9.     disp-ext-parm       = token "=" value  
    10.                        | ext-token "=" ext-value  
    11.    ext-token           = <the characters in token, followed by "*">  
    

第一反应，是看不懂的。能猜到的是，引号(")包起来代表的是必须要的内容。

第2行disposition-type后面的“*(”的意思是？

继续谷歌，在RFC 5234 3.6和3.8当中找到了答案，原文是这样的：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate\(-249.000000, -126.000000\)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)*的用法

在“*”号左右，可以有两个数字，两个数字代表着后面紧跟内容的最小重复次数与最大重复次数。

“*1(foo bar)”等价于“[foo bar]”，代表0个或者1个，即可有可无的意思。（与各种指令参数的写法是一样的。）

那么“*( ";" disposition-parm )”的意思则为，括号中的内容，可以没有，也可以有多个。

#### 1.3 filename中的中文字符

关于filename介绍的原文太长，我不摘抄，请查看引用链接2中的4.3小节，此处只列出我的理解。

当需要保存文件的时候，“filename”和“filename*”参数提供了文件名称，当“filename”和“filename*”同时存在时，只有“filename*”生效。

“filename*”允许使用非ISO-8859-1中的字符，它可用的编码在RFC 5987中定义。

我在Django中试了一下：
    
    
    resp = HttpResponse(file_obj.read())  
    resp['Content-Disposition'] = "inline; filename*=UTF-8''中文.pdf"  
    resp['Content-Type'] = 'application/pdf'  
    

浏览器中看到的内容如下：
    
    
    Content-Disposition: =?utf-8?b?aW5saW5lOyBmaWxlbmFtZSo9VVRGLTgnJ+S4reaWhy5wZGY=?=  
    

显然，是错误的，再搜了搜，看到Django中FileResponse有以下实现：
    
    
    # django.http.response.py  
      
    class FileResponse(StreamingHttpResponse):  
        """  
        A streaming HTTP response class optimized for files.  
        """  
          
        # ...  
          
        def set_headers(self, filelike):  
            """  
            Set some common response headers (Content-Length, Content-Type, and  
            Content-Disposition) based on the `filelike` response content.  
            """  
              
            # ...  
              
            if filename:  
                disposition = "attachment" if self.as_attachment else "inline"  
                try:  
                    filename.encode("ascii")  
                    file_expr = 'filename="{}"'.format(filename)  
                except UnicodeEncodeError:  
                    # 我的尝试，差了一个quote函数  
                    file_expr = "filename*=utf-8''{}".format(quote(filename))  
                self.headers["Content-Disposition"] = "{}; {}".format(  
                    disposition, file_expr  
                )  
            elif self.as_attachment:  
                # 如果没有名字，是只有前面内容的，与上面文档中看到的内容一致  
                self.headers["Content-Disposition"] = "attachment"  
    

浏览器中的Header变成以下内容：
    
    
    Content-Disposition: inline; filename*=UTF-8''%E4%B8%AD%E6%96%87.pdf  
    

点击“另存为”，弹出来确认框中的文件名称，变成了“中文.pdf”。

展示中文字符，需要quote一下。

至此，我对返回头Content-Disposition，有了些了解。

### 3\. 其它

这是我第一次尝试阅读RFC文档。RFC的全称是Request For Comments，它的简介如下：

> Request For Comments（RFC），是一系列以编号排定的文件。文件收集了有关互联网相关信息，以及UNIX和互联网社区的软件文件。RFC文件是由Internet Society（ISOC）赞助发行。基本的互联网通信协议都有在RFC文件内详细说明。RFC文件还额外加入许多在标准内的论题，例如对于互联网新开发的协议及发展中所有的记录。因此几乎所有的互联网标准都有收录在RFC文件之中。（摘自百度百科。）

通过RFC查询字段定义时，我发现RFC文档对于单词（"MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL"）的使用，都是有明确规定的。

以MUST举例：

> MUST This word, or the terms "REQUIRED" or "SHALL", mean that the definition is an absolute requirement of the specification. (MUST意味着，这个定义是规范的绝对要求，实现者必须实现该定义。)

尝试阅读RFC，让我对HTTP，又多了些了解——不管是Django或是Chrome，都是按标准办事的。

### 4\. 引用链接

  1. 一个关于Content-Disposition的讨论：https://stackoverflow.com/questions/1012437/uses-of-content-disposition-in-an-http-response-header
  2. RFC 6266：https://www.rfc-editor.org/rfc/rfc6266
  3. RFC 5234：https://datatracker.ietf.org/doc/html/rfc5234#page-9 <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247485136&amp;idx=1&amp;sn=0045722fe8002f870bffce6b3d19405b&amp;chksm=a6c76a3d91b0e32bae7c069255c8d923f9cb211e3ec1145be47465ae3eea3064bc99433e9712" rel="noopener noreferrer">原文链接</a>）</small>