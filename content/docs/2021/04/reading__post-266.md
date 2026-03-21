---
title: SQLite测试环境搭建
date: '2021-04-25'
weight: 291040266
primary_category: reading
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484023&idx=2&sn=59123201490c4864d76bcbf7e94a460d&chksm=a6c76e9a91b0e78c3fd4e78c7adf671aa311bfc96f2589f96503abfa48fe58486e0433dbc094
---
## SQLite的使用入门

从SQLite官网下载页面下载**sqlite-tools-win32-x86-3350100.zip** 。解压之后，得到三个文件：  


  * sqlite3.exe

  * sqldiff.exe

  * sqlite3_analyzer.exe




将文件夹加入环境变量。

从作者网站下载所提供的数据文件，在对应目录看看表：
    
    
    >sqlite3 tysql.sqlite  
    SQLite version 3.35.1 2021-03-15 16:53:57  
    Enter ".help" for usage hints.  
    sqlite> .tables  
    Customers   OrderItems  Orders      Products    Vendors  
    

看看数据：  

    
    
    sqlite> select cust_id from Customers;  
    1000000001  
    1000000002  
    1000000003  
    1000000004  
    1000000005  
    

到此处，测试环境搭建完毕，可以跟着书中一起尝试SQL指令啦。

## SQLiteSutdio的使用

看书到中途，发现sqlite3在命令行模式下面，数据展示的格式不好看。

一番搜索，选择图形化界面SQLiteSutdio，下载下来，不需要安装，直接打开exe，把数据库拖进去，结果看起来清爽许多：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate\(-249.000000, -126.000000\)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

## Python中使用数据库

直接按照官方文档的来一发：  

    
    
    # -*- coding: utf-8 -*-  
      
    # 这个是Python自带的模块，不需要额外安装  
    import sqlite3  
      
    def main():  
            # 必须得先建立一个连接，连接上数据库  
    	con = sqlite3.connect('tysql.sqlite')  
    	# 然后需要一个游标，来执行函数  
    	cur = con.cursor()  
    	# 执行具体的SQL语句  
    	for row in cur.execute('select prod_id, quantity, item_price, quantity*item_price as expanded_price from OrderItems where order_num = 20008;'):  
    		print(row)  
    		  
    	# con.commit()  
    	# 关闭数据库，关闭之前必须得commit一下  
    	con.close()  
      
      
    main()  
    

执行结果如下
    
    
    ..>py -2 test.py  
    (u'RGAN01', 5, 4.99, 24.950000000000003)  
    (u'BR03', 5, 11.99, 59.95)  
    (u'BNBG01', 10, 3.49, 34.900000000000006)  
    (u'BNBG02', 10, 3.49, 34.900000000000006)  
    (u'BNBG03', 10, 3.49, 34.900000000000006)  
      
    ..>py -3 test.py  
    ('RGAN01', 5, 4.99, 24.950000000000003)  
    ('BR03', 5, 11.99, 59.95)  
    ('BNBG01', 10, 3.49, 34.900000000000006)  
    ('BNBG02', 10, 3.49, 34.900000000000006)  
    ('BNBG03', 10, 3.49, 34.900000000000006)  
    

o了k，这就可以了。

## 参考链接

  1. sqlite官网下载，https://www.sqlite.org/download.html

  2. sqlite快速使用，https://www.sqlite.org/quickstart.html

  3. 作者书中的测试内容，https://forta.com/books/0672336073/

  4. sqlite工具介绍，https://blog.csdn.net/qq_29428215/article/details/86133946

  5. SQLiteSutdio，https://sqlitestudio.pl/

  6. Python使用sqlite，https://docs.python.org/3.10/library/sqlite3.html?highlight=sqlite3#module-sqlite3 <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247484023&amp;idx=2&amp;sn=59123201490c4864d76bcbf7e94a460d&amp;chksm=a6c76e9a91b0e78c3fd4e78c7adf671aa311bfc96f2589f96503abfa48fe58486e0433dbc094" rel="noopener noreferrer">原文链接</a>）</small>