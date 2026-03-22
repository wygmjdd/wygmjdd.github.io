---
title: awk告诉我，老詹得了多少分
date: '2020-12-20'
weight: 292300007
primary_category: technical-blog
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247483831&idx=1&sn=4bb24232eb8a0eecb73479d57ea6e186&chksm=a6c76d5a91b0e44ca08505bc686be0785403ab38aedd037c01c11f2742f3bf181811ac798fe3
---
游戏刚上线期间，某天写出一个bug，导致许多玩家多拿许多奖励。确认问题在线修复后，需要将这些奖励追回。当时老大在Linux下面刷刷刷的将刷奖玩家统计完毕，而我只能使用可视化工具导出数据、不熟练的捣鼓Excel表。感受到能力不足，事情处理完毕后，怒学一波！

awk能用来做什么呢？

总结时，NBA季后赛正进行中。便在维基百科获取了2020年全明星名单，自己随意定点规则，生成一些log，进行分析。

将一场比赛切分为48*60*10=28800个0.1秒，球员会在某个0.1秒得分，得多少分从[1，2，3]中随机选择一个值。

生成出来的log格式如下：
    
    
    # 时间、东西部、号码、名字、城市、队伍、得分、得分时刻  
    2020-09-07 17:01:02 eastern num 3 Joel Embiid from Philadelphia 76ers got 3 score, at forth quarter 11:30.1  
    2020-09-07 17:01:02 western num 10 Chris Paul from Oklahoma City Thunder got 1 score, at forth quarter 09:46.6  
    ...  
    

#### **每个球员的总得分**
    
    
     # 指令整体  
    cat score.log | awk -F ' num ' '{print $2}' | awk -F ' score,' '{print $1}' | awk -F ' got ' '{a[$1] += $2} END{for(i in a) print a[i], i}' | sort -rn  
    

分步骤看下使用的指令。

##### **1\. 拿到文件，第一次拆分**
    
    
    cat score.log | awk -F ' num ' '{print $2}'  
      
    # 显示文件内容  
    cat score.log  
      
    # awk的处理内容为`$cat$`的输出，一行一行的处理  
    # -F指定行中分隔符，以' num '作为分隔符将输入内容拆分为很多部分，此处只会拆分为两部分  
    # print $2打印拆分后的第二部分  
    awk -F ' num ' '{print $2}'  
    

结果（过程中的结果，只复制头两行，看看格式就好）为
    
    
    3 Joel Embiid from Philadelphia 76ers got 3 score, at forth quarter 11:30.1  
    10 Chris Paul from Oklahoma City Thunder got 1 score, at forth quarter 09:46.6  
    

##### **2\. 第二次拆分**
    
    
     # 同上，awk继续处理上一次awk的输出内容，指定分隔符，拆分得到两部分内容，打印出第一部分  
    awk -F ' score,' '{print $1}'  
    
    
    
    3 Joel Embiid from Philadelphia 76ers got 3  
    10 Chris Paul from Oklahoma City Thunder got 1  
    

##### **3\. 第三次拆分，并进行统计**
    
    
     # 1. 继续拆分，得到名字($1)与单次得分($2)  
    # 2. a是一个dict，名字为key，一行一行的输入，名字相同的得分累加。  
    # 3. END关键字后跟着的内容，在整个文件处理结束后执行。我这里执行的动作是，将数组a中的内容，进行打印  
    awk -F ' got ' '{a[$1] += $2} END{for(i in a) print a[i], i}'  
    
    
    
    79340 6 Kyle Lowry from Toronto Raptors  
    79510 2 Ben Simmons from Philadelphia 76ers  
    ...  
    80138 5 Damian LillardINJ1 from Portland Trail Blazers  
    79504 2 Khris Middleton from Milwaukee Bucks  
    

##### **4\. 排序**
    
    
     # 按照分数进行逆向排序  
    sort -rn  
    

得到最终结果。咦，这次的100w执行，竟然是保罗得分最高，运气好哦。（每个人的得分总数都很是接近，后面有必要改进一下随机规则。）
    
    
    80920 10 Chris Paul from Oklahoma City Thunder  
    80763 4 Kemba Walker from Boston Celtics  
    ...  
    79340 6 Kyle Lowry from Toronto Raptors  
    79204 4 Kawhi Leonard from Los Angeles Clippers  
    

#### **每个人的绝杀次数**

我这里定义的绝杀：每场比赛的最后0.5秒得分，就算一次绝杀。
    
    
    # 指令整体  
    cat score.log | awk '/at forth quarter 11:59/' | awk -F 'at forth quarter 11:59.' '{if($2>4) print $1, (10-$2)/10}' | awk -F ' num ' '{print $2}' | awk -F ' score,' '{print $1}' | awk -F ' got ' '{a[$1] += $2} END{for(i in a) print a[i], i}' | sort -rn  
    

相较于上一条总得分，此条指令只是在上一条指令前添加了一些筛选。继续按步骤说说看。

##### **1\. 筛选最后一分钟**
    
    
     # awk的正则，匹配第4节的最后一分钟  
    cat score.log | awk '/at forth quarter 11:59/'  
    
    
    
    2020-09-07 17:01:02 western num 2 Nikola Jokić from Denver Nuggets got 1 score, at forth quarter 11:59.9  
    2020-09-07 17:01:02 eastern num 1 Pascal Siakam from Toronto Raptors got 3 score, at forth quarter 11:59.9  
    

##### **2\. 筛选出最后0.5秒内容**
    
    
     # 分割出秒数的小数点，如果大于4，那么就属于最后的0.5秒。打印出出手时刻  
    awk -F 'at forth quarter 11:59.' '{if($2>4) print $1, (10-$2)/10}'  
    
    
    
    2020-09-07 17:01:02 western num 2 Nikola Jokić from Denver Nuggets got 1 score,  0.1  
    2020-09-07 17:01:02 eastern num 1 Pascal Siakam from Toronto Raptors got 3 score,  0.1  
    

##### **3\. 使用之前步骤统计出结果**
    
    
    24 16 LeBron James from Los Angeles Lakers  
    19 1 Rudy Gobert from Utah Jazz  
    

这下，绝杀次数，是老詹的最多了。时间缩短些，最后0.1秒得分最多的是西亚卡姆。

#### **老詹在第4节得了多少分**
    
    
     # 数据  
    # 2020-09-07 17:01:02 western num 16 LeBron James from Los Angeles Lakers got 1 score, at forth quarter 06:37.8  
      
    # 匹配老詹，匹配第4节；awk的默认拆分符号为空格，从左往右数第13个为得分，直接累加就好  
    cat score.log | awk '/16 LeBron James from/' | awk '/at forth quarter/' | awk 'BEGIN{a=0} {a += $13} END{print a}'  
    

最终结果为：20172分。

#### **小小总结**

目前已经能够比较快的统计出想要数据，不过awk还有许多高级用法。先到此处，且在未来的运用中继续熟悉。

说说看我的学习过程：

> 看见别人用，复制过来指令，修修改改，得出一个结果。
> 
> 遇见模糊内容，查询每个指令的具体用法。
> 
> 多多练习，记笔记，搞不定的时候。继续学习awk。
> 
> 持续多次使用。
> 
> 查看一个完整的awk教程。（我认为这一篇整理的最好：http://www.zsythink.net/archives/tag/awk/）

#### **附上生成数据的Python代码**
    
    
     # -*- coding: UTF-8 -*-  
    # gen_awk_data.py  
      
    import random, time  
      
    MINUTE_PRICISION = 60 * 10                              # 一分钟的精度  
    ONE_GAME_DURATION = 48 * MINUTE_PRICISION  
    QUARTER_DURATION = 12 * MINUTE_PRICISION  
    QUARTER_NAME = { 0: "first", 1: "second", 2: "third", 3: "forth" }  
      
    PLAYER_INFO = [  
            ('eastern', 'G', 'Kemba Walker', 'Boston Celtics', 4),  
            ('eastern', 'G', 'Trae Young', 'Atlanta Hawks', 1),  
            ('eastern', 'F', 'Giannis Antetokounmpo', 'Milwaukee Bucks', 4),  
            ('eastern', 'F', 'Pascal Siakam', 'Toronto Raptors', 1),  
            ('eastern', 'C', 'Joel Embiid', 'Philadelphia 76ers', 35),  
            ('eastern', 'G', 'Kyle Lowry', 'Toronto Raptors', 6),  
            ('eastern', 'G', 'Ben Simmons', 'Philadelphia 76ers', 2),  
            ('eastern', 'G', 'Jimmy Butler', 'Miami Heat', 5),  
            ('eastern', 'F', 'Khris Middleton', 'Milwaukee Bucks', 2),  
            ('eastern', 'F', 'Bam Adebayo', 'Miami Heat', 1),  
            ('eastern', 'F', 'Jayson Tatum', 'Boston Celtics', 1),  
            ('eastern', 'C', 'Domantas Sabonis', 'Indiana Pacers', 1),  
            ('western', 'G', 'James Harden', 'Houston Rockets', 86),  
            ('western', 'G', 'Luka Dončić', 'Dallas Mavericks', 1),  
            ('western', 'F', 'LeBron James', 'Los Angeles Lakers', 16),  
            ('western', 'F', 'Kawhi Leonard', 'Los Angeles Clippers', 4),  
            ('western', 'C', 'Anthony Davis', 'Los Angeles Lakers', 7),  
            ('western', 'G', 'Chris Paul', 'Oklahoma City Thunder', 10),  
            ('western', 'G', 'Russell Westbrook', 'Houston Rockets', 9),  
            ('western', 'G', 'Damian LillardINJ1', 'Portland Trail Blazers', 5),  
            ('western', 'G', 'Donovan Mitchell', 'Utah Jazz', 1),  
            ('western', 'F', 'Brandon Ingram', 'New Orleans Pelicans', 1),  
            ('western', 'C', 'Nikola Jokić', 'Denver Nuggets', 2),  
            ('western', 'C', 'Rudy Gobert', 'Utah Jazz', 1),  
            ('western', 'G', 'Devin BookerREP1', 'Phoenix Suns', 1)  
    ]  
      
    def getStrftime():  
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  
      
    def getScoreTime(scoreTime):  
            quarter = scoreTime / QUARTER_DURATION  
            quarterTime = scoreTime - (QUARTER_DURATION * quarter)  
            minute = quarterTime / MINUTE_PRICISION  
            second = quarterTime % MINUTE_PRICISION / 10  
            decimal = quarterTime % MINUTE_PRICISION % 10  
            if decimal != 0:  
                    return "%s quarter %02d:%02d.%d" % (QUARTER_NAME.get(quarter), minute, second, decimal)  
            else:  
                    return "%s quarter %02d:%02d" % (QUARTER_NAME.get(quarter), minute, second)  
      
    def genOneLog():  
            player = random.choice(PLAYER_INFO)  
            score = random.choice([1, 2, 3])  
            scoreTime = getScoreTime(random.randint(1, ONE_GAME_DURATION))  
      
            return '%s %s num %s %s from %s got %s score, at %s\n' % (getStrftime(), player[0], player[4], player[2], player[3], score, scoreTime)  
      
    def genLogs():  
            with open('score.log', 'w') as f:  
                    for _ in xrange(1000000):  
                            f.write(genOneLog())  
      
    if __name__ == '__main__':  
            genLogs() <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247483831&amp;idx=1&amp;sn=4bb24232eb8a0eecb73479d57ea6e186&amp;chksm=a6c76d5a91b0e44ca08505bc686be0785403ab38aedd037c01c11f2742f3bf181811ac798fe3" rel="noopener noreferrer">原文链接</a>）</small>