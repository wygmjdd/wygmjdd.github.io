---
title: 读完一本书，发现自己知道的好少~
date: '2021-04-25'
weight: 291040194
primary_category: reading-category
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484023&idx=1&sn=0b9c688edb306e6a173ada4a8c310022&chksm=a6c76e9a91b0e78c057a9c0bca917ef631848e3475264171fe6e9bd3483e0ef0edf90c5779c9
---

## 阅读动机

最近做的一个系统，需要频繁地更新数据库，不熟悉许多的数据库指令，总是谷歌或找个示例抄一下。此种方式能够将功能实现，但在代码与数据库之间，似乎总有一层薄纱，挡在我的眼前，我想将这薄纱移掉。

（不熟悉，似乎才是正常的。因为数据库相关的知识，只在大学，跟着课程学习过一学期。工作之后使用次数也不多，每次使用都是照猫画虎。）

从最基础的开始，找到书籍《Sams Teach Yourself SQL in 10 Minutes》（中文翻译为《SQL必知必会》）。开始阅读之前，先看看作者对书籍的介绍：

> This is the best selling SQL book of all time, and is used by individuals, organizations, and as courseware by dozens of academic institutions the world over. This book was born out of necessity. I had been teaching and writing on SQL for a long time, but whenever I was asked to recommend a good book on SQL I found myself somewhat stuck. There are good SQL books out there, but most of them are oriented towards database administrators or developers working within a highly database and SQL-centric world. And as such, most of them are overkill – they tend to provide too much information instead of just what most of us need to know. （这是最最畅销的SQL书籍，被很多的个人、机构、大学所使用。作者教授多年SQL，当被问到推荐一本SQL的书籍时，不知道推荐哪一本。市面上有很多好书，大部分面向的读者是数据库管理员、以SQL为工作重心的开发者。杀鸡焉用宰牛刀！大部分开发者，并不需要知道太多。）

这是一本专门针对一线软件开发人员的入门书籍，讲述实际工作环境中最常用和最必须的SQL知识，实用性极强。

没错，这正好适合我——一位数据库的生手，赶紧读起来。

## 书籍概要

全书22个章节，每天看一点，历时27天阅读完毕。（嗯，解锁了新成就——人生中第一次完整读完一本英文书籍。）

阅读完毕后，我将本书分为四个部分。

#### 一、基本介绍

只有第一章，介绍了数据库与SQL的基本概念。

  * 数据库应用于各种各样的系统中，银行、购物、游戏，可以说，只要有数据的地方，就有数据库。

  * SQL全称为Structured Query Language（结构化查询语言），是一门编程语言，它负责数据的增删改查，被各式各样的DBMS（Database Management System，数据库管理系统）各自实现。




#### 二、查询

占据了13章的篇幅，全部是查询相关的内容。查询、筛选、排序、函数调用、计算、归纳、连接等等。

#### 三、增删改

篇幅只有3章，插入数据占一章，删与改占一章，表的增删改占一章。

#### 四、高端内容

拆分为4章，依次讲述View（视图）、Stored Procedures（存储过程）、Transaction Processing（事务处理）、Cursors（游标）。

最后一章，介绍SQL的一些进阶特性，主要包括Constraints（约束）、Indexes（索引）、Triggers（触发器）以及Security（安全性）。

\--

此处简单地列举了书籍框架。另外整理了一篇SQL调用（放在第三篇），供自己查阅。

侯捷老师说：

> 从事写作，有一件事非常要紧，就是资料的收集与整理。我所认识的一些有点成绩的朋友，他们都有自己一套收集整理数据的系统，他们都深知这件事情的重要性。注意，数据的收集固然重要，到底不会太难，杂志、书籍、文件，最多不过花点钱，网络 (BBS 和 Internet)更容易让你的数据爆炸；更重要的是，整理的工夫。一百份整理过的数据，价值高于一万份未经整理的资料；未经自己整理的资料，和垃圾没有两样。

敲了这么多年代码，我感觉对于敲代码来说，资料的整理也很重要。将书籍阅读一遍后，脑子中留了印象。待到真正在代码中使用，对于不确定的点，翻翻笔记，翻翻书，是极有效率的。

## 小小感悟

大白鹅在工作一年多之后曾经说过：“以前大学学C语言的时候感觉老难了~现在感觉好简单，不知道大学是咋回事！”重新学习一遍SQL，我亦有相似感受。

当年学习过程中只感到“生涩”，装一个SQL Server需要折腾好几天，建一个数据库要点好久，敲一行指令要好几遍……

如今呢？有一点不一样，学习的速度快了许多。阅读本书的过程中经常触类旁通、豁然开朗、原来如此、小菜一碟。

不过！待阅读完毕，搜索“数据库的进阶之路”，发现我又井底之蛙、百思莫解、如堕烟海了。数据库的知识，还深着呢，可真是学海无涯啊！

\--

书中所讲述内容为关系型数据库的基础知识，而我此前工作中所使用的DBMS是MongoDB，隶属于NoSQL。本书只在夯实基础，要掀开那层薄纱，还得再找一本MongoDB的书看看~

## 参考链接

  1. 书籍对应官网，https://forta.com/books/0135182794/

  2. 豆瓣简介，https://book.douban.com/subject/24250054/
