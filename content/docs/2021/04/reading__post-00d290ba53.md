---
title: 供自己查阅的SQL手册
date: '2021-04-25'
weight: 291040000
primary_category: reading
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484023&idx=3&sn=470abc1b05cb80a4dbfe0245b2aa87d9&chksm=a6c76e9a91b0e78cf4a31a5b11582910246158dce415b6277287be8eebf33a42976f786d27ee
---
将书中的示例，都跟着走了一遍之后，将一些SQL语句、概念性的东西，记在这里，使用的时候快速翻阅。

## 查询

#### 不加筛选的查询
    
    
    -- 最简单的查询  
    select prod_id, prod_name, prod_price from Products;  
      
    -- 查询去重，每一项只列举一次  
    select distinct vend_id from Products;  
      
    -- 查询结果个数限制，从哪里开始  
    select distinct vend_id, prod_price from Products limit 2 offset 3;  
    

#### 对结果排序
    
    
    -- order by可以对多个键排序，得放在最后面  
    select prod_name,prod_price from Products order by prod_price, prod_name;  
      
    -- 可以按照位置排序  
    -- 优点：少打几个字  
    -- 缺点有点多：可能指定错误，前面顺序变了后面忘了变，不能使用不在查询列表的列  
    select prod_name,prod_price from Products order by 2, 1;  
      
    -- desc降序、asc升序  
    -- 如果要对多列进行降序升序选择，每一列分开指定  
    select prod_price,prod_name from Products order by prod_price desc;  
    

#### 条件筛选
    
    
    -- 能由数据库做的尽量都交给数据库做，有两个好处  
    -- 提高应用程序效率，减少数据传输  
    select prod_name, prod_price from Products where prod_price = 3.49;  
      
    -- and 与 or  
    select prod_name, prod_price from Products where vend_id = 'DLL01' or vend_id = 'BRS01' and prod_price >= 10;  
      
    -- in，用in会有些好处  
    -- 可读性、and和or同时存在，用in更好评估顺序、in的列表可以是查询的结果  
    select prod_name, prod_price from Products where vend_id in ('DLL01','BRS01');  
    

#### 模糊条件筛选
    
    
    -- 前面是Fish，后面什么无所谓  
    select prod_id, prod_name from Products where prod_name like 'Fish%';  
      
    -- 前后什么都无所谓，包含bean bag就好  
    select prod_id, prod_name from Products where prod_name like '%bean bag%';  
      
    -- 用_符号卡一个字符位置  
    select prod_id, prod_name, prod_desc from Products where prod_desc like '____测试中文';  
      
    -- []中的内容多选一，与正则中一样  
    select cust_contact from Customers where cust_contact like '[JM]%';  
    

使用通配符会耗费更多的时间，作者给了注意事项：

  * 不要过度使用通配符，能用普通的搞就用普通的搞，

  * 用的时候，不要放在第一个条件，

  * 小心使用，用错了，不会返回结果的，

  * 得根据具体的DBMS文档来，有些可能不支持。




#### 数据拼接
    
    
    -- 把多个数据拼在一起，不同DBMS使用的符号可能不同  
    select vend_name || '(' || vend_country || ')' as vend_title from Vendors order by vend_name;  
    

#### 函数调用

一般的DBMS会提供的函数

  * 文本操作，截断、拓展、大小写转换，

  * 数字运算，绝对值、加减乘除，

  * 时间函数，

  * 系统函数，返回具体DBMS使用的信息。



    
    
    select vend_name, upper(vend_name) as up from Vendors order by vend_name;  
    

#### 聚合函数

  * avg(), 列的平均值，

  * count(), 列的数量，

  * max()，列的最大值，

  * min()，列的最小值，

  * sum()，对列求和。



    
    
    select count(*), min(prod_price), max(prod_price), avg(prod_price) from Products;  
    

#### 数据分组
    
    
    -- 每个客户有多少个产品  
    select vend_id, count(*) as num_prods from Products group by vend_id;  
      
    -- where筛选rows，having筛选groups，having支持所有的where操作  
    select vend_id, count(*) as num_prods from Products where prod_price >= 4 group by vend_id having count(*) >= 2;  
    

#### 嵌套查询
    
    
    -- 还可以多层嵌套的  
    select cust_id from Orders where order_num in (select order_num from OrderItems where prod_id = 'RGAN01');  
    

#### join

把不同表的数据，同时查出来，比嵌套查询效率高。
    
    
    select prod_name, vend_name, prod_price, quantity from OrderItems, Products, Vendors  
        where Products.vend_id = Vendors.vend_id and OrderItems.prod_id = Products.prod_id and order_num = 20007;  
          
    -- 使用别名  
    select cust_name, cust_contact from Customers as C, Orders as O, OrderItems as OI  
        where C.cust_id = O.cust_id  
        and OI.order_num = O.order_num  
        and prod_id = 'RGAN01';  
    

outer join和inner join的区别
    
    
    -- inner join，都有数据的，才会返回  
    select C.cust_id, O.order_num from Customers as C inner join Orders as O  
        on C.cust_id = O.cust_id;  
          
    -- outer join，只要左边能找到，就列出来；右边找不到，列出空内容  
    select C.cust_id, O.order_num  
        from Customers as C left outer join Orders as O  
        on C.cust_id = O.cust_id;  
    

总结一下join的关键点

  * 注意join的使用类型。inter和outer的区别，

  * DBMS的具体join语法，

  * 确保使用了正确的join条件，

  * 确保总是提供join条件，

  * 使用join之前，可以将各个条件分别使用一番。




#### union
    
    
    -- 直接把不同的查询一起输出  
    select cust_name, cust_contact, cust_email  
        from Customers as C  
        where cust_state in ('IL', 'IN', 'MI')  
        union  
        select cust_name, cust_contact, cust_email  
        from Customers  
        where cust_name = 'Fun4All';  
    

## 增删改
    
    
    -- 基础插入  
    insert into Customers  
        (cust_id, cust_name, cust_address, cust_city, cust_state, cust_zip, cust_country, cust_contact, cust_email)  
        values('1000000007', 'Toy Land1', '123 Anya Street', 'Newa York', 'NY', '11111', 'USDA', NULL, NULL);  
          
    -- 从一个表搬到另一个表  
    insert into CustNew(cust_id, cust_contact, cust_email, cust_name, cust_address, cust_city, cust_state, cust_zip, cust_country)  
        select cust_id, cust_contact, cust_email, cust_name, cust_address, cust_city, cust_state, cust_zip, cust_country from Customers  
        where cust_id in ('1000000006', '1000000007');  
    

修改、删除行为准则：

  * 永远不要执行一个没有where的语句，除非你真的要操作所有，

  * 保证每个表都有主键，

  * 使用where之前，可以先用select测试是否正确，

  * 使用数据库的强制规则保证完整性（enforced referential integrity），

  * 有些DBMS是支持给delete、update加约束（比如必须有where）的，如果有，用上。



    
    
    -- update  
    update Customers set cust_contact = 'Sam Roberts', cust_email = 'sam@toyland.com' where cust_id  = '1000000006';  
    
    
    
    delete from Customers where cust_id = '1000000006';  
    

#### 创建、删除表

作者建议创建可以使用图形化界面，相较于敲指令，会更方便一些。
    
    
    -- 创建  
    create table Test1  
        (name char(10) not null,  
        age decimal(8, 2) not null  
        );  
          
    -- 修改  
    alter table Test1 add phone char(11);  
      
    -- 删除  
    drop table Test2;  
    

## 高级内容

view是虚拟表，不包含数据，只在SQL语句真正执行的时候才查询需要数据。使用原因：

  * 重用SQL语句，

  * 简化复杂的SQL操作，

  * 只暴露部分表格，

  * 数据保护，可以设定用户只访问指定数据，

  * 改变数据格式和表现。



    
    
    -- 创建视图  
    create view ProductCustomers as  
        select cust_name, cust_contact, prod_id  
        from Customers, Orders, OrderItems  
        where Customers.cust_id = Orders.cust_id and OrderItems.order_num = Orders.order_num;  
          
    -- 使用视图  
    select cust_name, cust_contact from ProductCustomers where prod_id = 'RGAN01';  
    

#### Stored Procedures

存储过程，代码重用，与DBMS强关联，基本上大佬写，小弟用。哈哈。
    
    
    -- oracle下面创建  
    CREATE PROCEDURE MailingListCount (  
        ListCount OUT INTEGER   
    )  
    IS  
    v_rows INTEGER;  
    BEGIN  
        SELECT COUNT(*) INTO v_rows  
        FROM Customers  
        WHERE NOT cust_email IS NULL;  
        ListCount := v_rows;  
    END;  
      
    -- oracle下面使用  
    var ReturnValue NUMBER  
    EXEC MailingListCount(:ReturnValue);  
    SELECT ReturnValue;  
    

#### Transaction Processing

事务处理，保证SQL批量操作能够完整（部分完整）执行。

#### Cursors

游标，一坨从数据库查询出来的缓存数据。可以前后挪动查看结果。

#### Advanced SQL Features

Constraints，主键、外键、数据唯一性、指定条件，都是约束。

Indexes，提升查找、排序的速度，类似书籍的页码。

Triggers，特殊的存储过程，某些情况发生的时候，触发执行一下。

Security，数据库的安全管理。 <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247484023&amp;idx=3&amp;sn=470abc1b05cb80a4dbfe0245b2aa87d9&amp;chksm=a6c76e9a91b0e78cf4a31a5b11582910246158dce415b6277287be8eebf33a42976f786d27ee" rel="noopener noreferrer">原文链接</a>）</small>