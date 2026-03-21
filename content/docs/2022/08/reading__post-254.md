---
title: 一篇关于B+树的读书笔记
date: '2022-08-08'
weight: 286340254
primary_category: reading
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247485013&idx=1&sn=6d00597498bc6da952e90fbda2b255dc&chksm=a6c76ab891b0e3aec82efa3912dabd3365fa95d78385def60eb1e475b0e25b057ec99c41314a
---

将睡觉时间改为强制11点后，每天早上是自然醒的，自然醒之后的时间，被我用来完成一个番茄钟——阅读《数据库系统概念》。

6月中旬，读到第11章“索引与散列”，其中有一节是B+树。阅读之前，对B+树，我是有些恐惧的——我的学习历史告诉我，这东西很难，很难搞懂。

阅读之后，更新和删除，我依然不能用自己的语言整理出来；但我对B+树有了了解，于是将此篇读书笔记进行分享，记一次从恐惧到坦然。

# 笔记

> We design additional structures that we associate with files.（索引是为更快的文件访问而设计的。）

## 11.3 B+-Tree Index Files

直接摘抄，不自己总结。

> The main disadvantage of the index-sequential file organization is that performance degrades as the file grows, both for index lookups and for sequential scans through the data. Although this degradation can be remedied by reorganization of the file, frequent reorganizations are undesirable. （顺序索引的主要不足是当文件增长后的性能下降，不管是索引搜索还是数据的顺序搜索。即便可以通过重组文件处理，但频繁重组并不可取。）
> 
> The **B+-tree** index structure is the most widely used of several index structures that maintain their efficiency despite insertion and deletion of data. A B+-tree index takes the form of a **balanced tree** in which every path from the root of the tree to a leaf of the tree is of the same length. （B+树索引因为增删高效，是几个索引结构中使用最广泛的，它每个节点到跟，都有相同长度。）
> 
> ...
> 
> Indeed, the “B” in B+-tree stands for “**balanced**.” It is the balance property of B+-trees that ensures good performance for lookup, insertion, and deletion. （我是一直不知道B是什么意思的，书给了我答案。B代表的是“平衡”，树的平衡性保证了增删查的性能。）

我得先去看看B+树的概念吧？

### B+树的结构

先去看了一篇博客，简单的了解一下B+树，但记不下来。

回来看书，关于节点的样子，我是看懂了的。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate\(-249.000000, -126.000000\)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)一个节点的样子

B+树是多级索引，与顺序索引的多级并不一样。

> Figure 11.7 shows a typical node of a B+- tree. It contains up to n − 1 search-key values , ,..., , and n pointers , ,..., . The search-key values within a node are kept in sorted order; thus, if i < j, then  < . （图11.7表述了一个B+树的节点，n-1个search key与n个指针，search key是排过序的。）

再去看了一下上面的博客，博客中附带了另一个网址，网址中有模拟B+树的插入。更形象的表达，我似乎懂得多了一点点。我应该对B+树的理解，整理一篇博客。因为在看它之前，我有些害怕，怕自己看不懂。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate\(-249.000000, -126.000000\)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)一棵B+树的样子![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate\(-249.000000, -126.000000\)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)更胖一点的B+树样子

看到这里，我对树的样子，有了概念，为什么要做成树呢？模糊的知道，这样子搜索起来，应该挺快的。那占用存储空间的大小呢？如何计算呢？

存储空间，一个数组，中间有search key和指针。search key的大小由应用决定，指针是8字节。所以，问题是，n的数量是如何确定下来的？且先往后看看查询和更新。

### B+树的查询

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate\(-249.000000, -126.000000\)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)B+树查询的伪代码

上面伪代码，我是看懂了的，跟着作者的思路走。

如果让我自己来写呢？

> 总是从一个节点P出发，在节点P中，通过比较目标值V与节点中存储的search key K，找到刚刚比V小的Ki，从而确定存储目标值的区间节点S，这个S是一条指针，跟在Ki后面。
> 
> S变成P，一直找找找。
> 
> 找到子节点后，还需要打印出所有的值。所有的值，是可能在相邻节点上面的。

是的，通过这个查询过程，我了解到B+树的值，总是存在叶子结点上。

哟，我上面的疑问，在这里有了答案。作者对大小、节点与深度计算做了举例。

> 节点大小，一般为磁盘块（disk block）大小，通常是4KB。
> 
> 如果search key的大小为12个Byte，指针大小为8个，则。n约为200，一个节点上面可以存200条指针，199个search key。search key再大点，如变成32个Byte，则能存约100个。
> 
> 设n=100，search key有100万个。一次查找最多只需要从磁盘读次。根节点往往都在内存中。
> 
> B+树胖而矮，二叉树瘦而高。数据库性能瓶颈在于访问磁盘，访问磁盘次数越少越好，故选用B+树。

而同时呢，又有一个新的疑问出现。此刻我理解了B+树的结构与查询，多久之后我会忘记呢？忘记之后，重新再来看读书笔记，能再次很快地理解么？

初高中，我很喜欢化学，对那些分子式都记得熟熟的，似乎掌握了化学反应的规律；现在，连元素周期表都已经背不下来。所以忘记，是肯定会的。那问题应该来到如何能够捡起来？如何能够快速地捡起来？

（此处可能有另一种说法？忘记是因为我还没有就这个事情理透？骑自行车、游泳，学会了就不会忘记，怎么到B+树这里就会忘记呢？嘿，这又是一个话题，我得去找找看。）

我相信这读书笔记是会有帮助的。有更好的方式么？

对了，还有另外一个点，关于“我此刻的理解”，在读本章之前，我一直以为B+树很难，因为我以前看过B+树，看过树，我觉得树对我来说，相当难以理解。跟着书中走，似乎理解起来并没有那么难。这中间的差异是？

之前的树学习，只是一个概念，是很多数据结构中的一种，我不知道它能用来做什么，于是便想在脑子中来构造它的作用，而我构造不出来。现在跟着书，我知道我们的目标是维护一个多级索引，让访问磁盘的次数少些，而树，是能满足我们的目标的。或许B+树，就是为此而生？

另外，一个页节点存储为一根指针Pn，这个Pn指针指向下一个块。内存中的指向我能想象，那当存储到磁盘之后是如何表现的呢？问准确一点，内存中的内容，是如何一一映射到硬盘中去的呢？指针会转换么？

### B+树的更新

旧记录的更新 = 先删再加。

> Insertion and deletion are more complicated than lookup, since it may be necessary to **split** a node that becomes too large as the result of an insertion, or to **coalesce** nodes (that is, combine nodes) if a node becomes too small (fewer than [n/2] pointers). （增删需要分裂节点或者合并节点，所以比查更复杂。）

由上，增删会有两种形式，一是数据量不大，不需要分裂或者合并时。找到需要增删的节点，在节点内做增删就好。

但分裂与合并，是必须要有的。

（感觉这个看完之后，就真的能够对B+树有些了解了吧？学数据库，也是在学数据结构与算法？）

到这里，已经很吃力了……

#### Insertion（插入）

> We find that “Adams” should appear in the leaf node containing “Brandt”, “Califieri”, and “Crick.” There is no room in this leaf to insert the search-key value “Adams.” （一个节点已经满了。）

看上面图11.9说话，第一个节点已经装满，不能再插入新的索引项。看图过程中，按照上面查询里面的例子，这些数据应该是只需要存在一个4K节点上面的。故，图11.9只是举个例子吧？

为了回答自己的问题，我再去看了上面的博客。得出以下结论：

  1. 图11.9中的B+树，是一棵4阶的B+树。阶代表每个节点最多有的子节点数。（很讨厌这种名词定义，因为我总是记不住。除了“阶”，还有“度”，还有……）
  2. 4阶的树，每个节点的search key数量，最少为1个，最多是3个。由公式规定，n为阶数，k为search key数量，[]表示向上取整。指针（子节点）的数量区间，则为。
  3. 图11.9中指向Crick的那个箭头，应该修改为从Califieri与Crick之间出来。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate\(-249.000000, -126.000000\)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)节点一分为二![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate\(-249.000000, -126.000000\)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)将分裂的节点插入父节点![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate\(-249.000000, -126.000000\)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)再插入一个，造成非叶子结点的分裂![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate\(-249.000000, -126.000000\)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)插入的伪代码

#### Deletion（删除）

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate\(-249.000000, -126.000000\)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)从11.13图中删掉“Srinivasan”![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate\(-249.000000, -126.000000\)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)再删去两个节点![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate\(-249.000000, -126.000000\)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)再删一个![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate\(-249.000000, -126.000000\)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)删除节点的伪代码

### 引用链接：

  1. B+树的介绍：https://zhuanlan.zhihu.com/p/351240279
  2. B+树的可视化：https://www.cs.usfca.edu/~galles/visualization/BTree.html
