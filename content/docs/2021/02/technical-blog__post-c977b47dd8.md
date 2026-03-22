---
title: pythonw是什么？
date: '2021-02-28'
weight: 291600028
primary_category: technical-blog
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247483929&idx=1&sn=f10b9aabebd8f031845b6c7d8699222e&chksm=a6c76ef491b0e7e2489e71627a2b2be78666575380069c226ea670f3180507751ba20c1fe9d2
---
## pythonw是什么？

阅读Python源码的过程中，看到Py_main函数在两个地方被调用。其中一个为Project pythonw中的WinMain.c中。当build Project pythonw后，生成了文件pythonw_d.exe。

![图片](/images/wechat/c977b47dd8b7/001.png)

  


双击pythonw_d.exe之后什么都没有出现，于是好奇它是干嘛的。搜索一番之后看到下面这段对pythonw的使用
    
    
    # 将myApp中的调试信息输出到文件  
    >pythonw myApp.py 1>stdout.txt 2>stderr.txt  
    

有点理解到pythonw的作用：**pythonw与python功能一致，只是不打印输出错误信息。**

创建一个pyw文件，双击之后，Windows会弹出界面“**你要如何打开这个文件？** ”，默认推荐应用为pythonw.exe。

鼠标移到该文件上面，看到文件类型为：Python File(no console).

![图片](/images/wechat/c977b47dd8b7/002.png)

  


此时大概了解pythonw是什么。但是想看看Python官方是怎么说的，搜到标题为《PEP 397 -- Python launcher for Windows》的一篇指引文章，里面写到：

> The launcher comes in 2 versions - one which is a console program and one which is a "windows" (ie., GUI) program. These 2 launchers correspond to the 'python.exe' and 'pythonw.exe' executables which currently ship with Python. The console launcher will be named 'py.exe' and the Windows one named 'pyw.exe'. （启动器有2个版本，一个是控制台版本，一个是windows图形化版本。两个版本都是启动Python，他们被分别命名为'py.exe'和'pyw.exe'。）

pythonw=python+w，其中添加的“w”后缀，代表windows，pythonw用于图形化界面。（技术文章读起来好累，理解的可能还不准确。真的真的还要持续学习英语啊！）

## 创建一个窗口

后缀名为pyw的文件，跟图形界面有关系，PyQT就是这个东东？于是跟随一篇博客试试如何使用PyQT。

先创建一个文件，复制粘贴进去博客中的代码。
    
    
    # -*- coding: utf-8 -*-  
      
    import sys  
    from PyQt5.QtWidgets import QApplication, QWidget  
      
    if __name__ == '__main__':  
    	app = QApplication(sys.argv)  
    	w = QWidget()  
    	w.resize(250, 150)  
    	w.move(300, 300)  
    	w.setWindowTitle('Simple')  
    	w.show()  
    	  
    	print("window showed.")  
      
    	sys.exit(app.exec_())  
    

来吧，执行起来。
    
    
    # 囧，报了个错。随后伴随着一系列操作~  
    dir>py -2 open_window.pyw  
    Traceback (most recent call last):  
      File "open_window.pyw", line 4, in <module>  
        from PyQt5.QtWidgets import QApplication, QWidget  
    ImportError: No module named PyQt5.QtWidgets  
      
    # 不能使用python？用pythonw试试看。什么都没有发生  
    dir>pythonw open_window.pyw  
      
    # output中的内容为空  
    dir>pythonw open_window.pyw > output  
      
    # ----------------------------------#  
      
    # 装一下pyqt5吧  
    dir>pip install pyqt5  
    ERROR: Could not find a version that satisfies the requirement pyqt5 (from versions: none)  
    ERROR: No matching distribution found for pyqt5  
      
    # 不行？那换pip3试试看。哦，原来已经装过。  
    dir>pip3 install pyqt5  
    Requirement already satisfied: pyqt5 in c:\python36\lib\site-packages (5.11.3)  
    Requirement already satisfied: PyQt5_sip<4.20,>=4.19.11 in c:\python36\lib\site-packages (from pyqt5) (4.19.13)  
    

猜想应该是pyqt5只能在python3下面运行。谷歌没有搜到确定信息，在PyQt5的官方文档中找到介绍（老是喜欢先谷歌、百度一番，最后再查阅官方文档，为什么呢？）：

> PyQt5 supports the Windows, Linux, UNIX, Android, macOS and iOS platforms and requires Python v3.5 or later. (PyQt5 should also build against Python v2.7 and earlier versions of Python v3 using the legacy configure.py build script but this is unsupported.)（PyQt5支持很多平台，但是需要Python版本在3.5以上。当然，PyQt5也可以使用Python2.7或者3.5之前的版本，不过不推荐。）

那么，使用Python3再来试一下吧。
    
    
    # 使用Python3打开上述文件，成功打开一个名字叫Simple的小窗口  
    dir>py -3 open_window.pyw  
    window showed.  
      
    # 什么都没有发生  
    dir>pythonw open_window.pyw  
    # 还是什么都没有发生  
    dir>pythonw -3 open_window.pyw  
      
    # 窗口出现，脚本中的print语句并未打印  
    dir>pyw -3 open_window.pyw

![图片](/images/wechat/c977b47dd8b7/003.png)

一个可视化的对比出现在我的眼前，py和pyw的区别一眼就看见，py打印了“window showed.”，而pyw没有。  


## 参考链接

  1. https://www.python.org/dev/peps/pep-0397/

  2. https://blog.csdn.net/pythonw/article/details/74430328

  3. https://stackoverflow.com/questions/24835155/pyw-and-pythonw-does-not-run-under-windows-7/30310192#30310192

  4. https://xmfbit.github.io/2017/08/29/learn-pyqt/

  5. https://www.riverbankcomputing.com/static/Docs/PyQt5/introduction.html#pyqt5-components <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247483929&amp;idx=1&amp;sn=f10b9aabebd8f031845b6c7d8699222e&amp;chksm=a6c76ef491b0e7e2489e71627a2b2be78666575380069c226ea670f3180507751ba20c1fe9d2" rel="noopener noreferrer">原文链接</a>）</small>