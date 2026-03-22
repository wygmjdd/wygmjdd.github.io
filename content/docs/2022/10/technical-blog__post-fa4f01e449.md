---
title: 几个排序算法的实现
date: '2022-10-02'
weight: 285790002
primary_category: technical-blog
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247485111&idx=2&sn=7730e7806b5a75426a0dc8b14b03be71&chksm=a6c76a5a91b0e34c0d64cc9bc9415bc19a16e6ce802d610f73f3fdbdafc19b8a1e59b9bc3f0c
---
根据一篇博客（链接于末尾引用）的介绍，将各个排序算法，进行一遍实现，并能用自己的语言解释一番。

## 基础概念

**稳定与不稳定** ，如果两个相等的数字，排序完成后，原来在前面的还是在前面，则是稳定的，否则为不稳定。

**时间复杂度** ，如果某一种类型的排序，只需要一个循环就搞定，那么他的时间复杂度为，需要循环中再套循环，两个循环次数相同的时间复杂度为，次数不同为。

**空间复杂度** 与时间复杂度类似，只是执行次数，变成了需要的空间大小。

**数据准备**

使用Python打印出来9999个数据后，直接复制粘贴进去，进行测试。
    
    
    import random  
      
    def func():  
     nums = []  
     for i in xrange(0, 9999):  
      nums.append(str(random.randint(-99999, 99999)))  
      
     s = ','.join(nums)  
     print s  
    

**测试代码**
    
    
     #pragma once  
      
    #include <iostream>  
    #include <vector>  
    #include <time.h>  
    using namespace std;  
      
    class MySort {  
    public:  
     MySort() {}  
     ~MySort() {}  
      
     void bubble(vector<int> &);  
     void selection(vector<int> &);  
     void insertion(vector<int> &);  
     void shell(vector<int> &);  
     void merge(vector<int> &);  
     void quick(vector<int>&, int, int);  
     void heap(vector<int> &);  
       
     void test();  
      
    private:  
     void swap(int &a, int &b);  
     int oneQuick(vector<int>&, int, int);  
     void createHeap(vector<int> &, int);  
     void adjustHeap(vector<int> &, int, int);  
    };  
      
      
    void MySort::swap(int &a, int &b) {  
     if (a >= b) return;  
     int tmp = a;  
     a = b;  
     b = tmp;  
    }  
      
    void MySort::test() {  
     // 数字为上面Python生成结果复制进来，太长就不复制进行了，input与input1的内容一样  
     vector<int> input = {};  
       
     clock_t start1 = clock();  
     sort(input.begin(), input.end());  
     clock_t end1 = clock();  
     cout << "STL use time: " << (double)(end1 - start1) / CLOCKS_PER_SEC << "s" << endl;  
       
     // 对于不同排序函数的调用，C++语法的函数指针，应该是可以做到的，此处先不用这个，直接改代码测试  
     vector<int> input1 = {};  
     clock_t start = clock();  
     // bubble(input1);  
     // ...  
     selection(input1);  
     clock_t end = clock();  
     cout << "Bubble use time: " << (double)(end - start) / CLOCKS_PER_SEC << "s" << endl;  
       
     // 写归并排序的时候，发现应该检测一下我的排序是否正确，于是和STL的对比下  
     bool isRight = true;  
     for (size_t i = 0; i < input.size(); ++i) {  
      if (input[i] != input1[i]) {  
       isRight = false;  
       break;  
      }  
     }  
     cout << "Is my sort right: " << isRight << endl;  
    }  
      
    

## 1、冒泡排序

类似于冒泡泡，将最大的那个数，一步步换到最后面去。维基百科上面，对冒泡排序的说法是：

> 由于它的简洁，冒泡排序通常被用来对于程序设计入门的学生介绍算法的概念。

我就通过复习冒泡，再次入门吧。冒泡排序的实现：
    
    
    void MySort::bubble(vector<int> &input) {  
     for (size_t i = 0; i < input.size(); ++i) {  
      for (size_t j = i + 1; j < input.size(); ++j) {  
       swap(input[i], input[j]);  
      }  
     }  
    }  
    

执行耗时：

> STL use time: 0.013s  
> Bubble use time: 27.46s

可以看出来，这个差距不是一般的大！当数据更多的时候，肯定更加几何倍增加。

## 2、选择排序

感觉跟冒泡排序思路是一样的，区别在于选择排序，进行的交换少很多。
    
    
    void MySort::selection(vector<int> &input) {  
     for (size_t i = 0; i < input.size(); ++i) {  
      size_t minIndex = i;  
      for (size_t j = i + 1; j < input.size(); ++j) {  
       if (input[j] < input[i]) {  
        minIndex = j;  
       }  
      }  
      swap(input[i], input[minIndex]);  
     }  
    }  
    

执行耗时：

> STL use time: 0.014s  
> Selection use time: 24.902s

从结果来看，确实比冒泡排序快些。

## 3、插入排序

将自己的理解记一下：

  1. 从第1个数字开始，假装当前已经有序。
  2. 第2个位置上的数字，如果第1个数字小，则将其插入到前面去。
  3. 第3个数字和之前有序序列的末尾比较，如果比第2个数字小，将其插入到第2个数字前面。如果还比第1个数字小，则再插入到更前面。
  4. 第4到n个数字，执行前面的步骤。



下面的代码，与博客中的代码进行了对比，发现他的速度比我的更快，对比原因直接写在注释。
    
    
    void MySort::insertion(vector<int> &input) {  
     for (size_t i = 1; i < input.size(); ++i) {  
      for (size_t j = i; j > 0; --j) {  
       if (input[j] >= input[j - 1]) {  
        break;  
       }  
       else {  
        swap(input[j - 1], input[j]);  
          
        // 此处，我将swap换进来，用时为：27.843s  
        // 为什么会慢的原因，还没想清楚。我认为少了一次函数调用，应该会更快才对的？？？  
        // int tmp = input[j - 1];  
        // input[j - 1] = input[j];  
        // input[j] = tmp;  
       }  
      }  
      
      // 博客中的写法，用时为：14.181s  
      // 比我速度快的原因在于，这里的插入，一次只进行了一次赋值。  
      // 而我的版本，直接进行了交换，有3次赋值操作，导致速度差异  
      //int preIndex = i - 1;  
      //int current = input[i];  
      //while (preIndex >= 0 && input[preIndex] > current) {  
      // input[preIndex + 1] = input[preIndex];  
      // --preIndex;  
      //}  
      //input[preIndex + 1] = current;  
     }  
    }  
    

我的版本执行用时:

> STL use time: 0.017s  
> Insertion use time: 19.531s

可以看到，插入排序，速度比选择排序会快一点。

## 4、希尔排序

希尔排序，在我自己将整个算法写出来后，得出的结论是，这个排序算法，其实就是在插入排序外面又套一层循环。每个循环都做次插入排序，只是每次插入排序的数据，都只是原始输入的一部分。
    
    
    // 在最开始写这个的时候，竟然忘掉了插入排序怎么做的。直接一层循环在那里换，囧。  
    void MySort::shell(vector<int> &input) {  
     vector<int> seq = { 16, 10, 7, 3, 1 };  
     // 保证seq.size()趟排序  
     for (int interval : seq) {  
      // 挨个的换跨度为interval的数字  
      for (int intervalIndex = 0; intervalIndex < interval; ++intervalIndex) {  
      
       // shell排序为简单插入排序改进版，所以必定需要包含一个简单插入排序的  
       for (size_t i = intervalIndex + interval; i < input.size(); i += interval) {  
        int preIndex = i - interval;  
        int curVal = input[i];  
        while (preIndex >= 0 && input[preIndex] > curVal) {  
         input[preIndex + interval] = input[preIndex];  
         preIndex -= interval;  
        }  
        input[preIndex + interval] = curVal;  
       }  
      }  
     }  
    }  
      
    

执行用时：

> STL use time: 0.014s  
> shell use time: 1.137s

看到这个执行用时，我被惊讶到了，瞬间快了好多好多倍。突破后的时间复杂度，在代码中的体现，简直太明显了。按照博客所说，希尔排序的时间复杂度为。

不过我重新搜索了一下，希尔排序的时间复杂度跟选择的有关系。复习先看维基百科吧。

## 5、归并排序（Merge Sort）

此次实现，没有看别人的解答，全是自己慢慢的磨。从昨天下午（2020-6-21）的不想做题，到鼓励自己花半小时试试看，从而投入一小时写出骨架，被合并操作卡住。晚上睡觉之前灵光一闪，知道合并问题所在，今早将其处理掉，得出正确解答。

记录下来后，和维基百科上面**迭代版** 进行了对比，发现框架基本上一致。至于**递归版** ，先暂时不考虑。

不过还有一个待处理的问题，当数据量太大，内存不够的时候，分治法的归并，到底是如何将数据合起来的呢？还没想通，这个需要想通。

看到一篇介绍分治法的博客里面一段话，忽然意识到，使用归并排序处理大数据，当数据拆分小块并排好序后的合并，只需要每次从每个小块中拿一个数字出来，进行比较，把最小的数字存到硬盘。这就好使了，也就是归并排序的一个步骤。

引用一下让我茅塞顿开的原文：

> 这里我们的做法是每次读取待排序文件的10000个数据，把这10000个数据进行快速排序，再写到一个小文件bigdata.part.i.sorted中。这样我们就得到了50000个已排序好的小文件了。
> 
> 在有已排序小文件的基础上，我只要每次拿到这些文件中当前位置的最小值就OK了。再把这些值依次写入bigdata.sorted中。
    
    
    void MySort::merge(vector<int> &input) {  
     vector<int> tmp1;  
     for (int step = 1; step < input.size(); step *= 2) {  
      for (size_t i = 0; i < input.size(); i += (2 * step)) {  
       tmp1.clear();  
      
       if (step == 1) {  
        // 最开始，2个数字一组，将小的放前面  
        if (i + 1 < input.size()) {  
         swap(input[i], input[i + 1]);  
        }  
       }  
       else {  
        // 再将已经排过序的2组2个数字，合并为1组4个数字；2组4个数字，合并为1组8个数字；...  
        int indexL = i;  
        int indexR = i + step;  
        for (indexL; indexL < i + step && indexL < input.size(); ++indexL) {  
         while (indexR < i + 2 * step && indexR < input.size() && input[indexR] < input[indexL]) {  
          tmp1.push_back(input[indexR]);  
          ++indexR;  
         }  
         tmp1.push_back(input[indexL]);  
        }  
        // 卡的瓶颈在这里，因为我下面的while还加了一个限制条件：input[indexR] < input[indexL])  
        // 正确应该是当Left位置已经走完，只需要将right边的数字全扔进tmp就好  
        while (indexR < i + 2 * step && indexR < input.size()) {  
         tmp1.push_back(input[indexR]);  
         ++indexR;  
        }  
      
        for (int j = i; j < i + 2 * step && j < input.size(); ++j) {  
         input[j] = tmp1[j - i];  
        }  
       }  
      }  
     }  
    }  
    

执行用时：

> STL use time: 0.013s  
> Bubble use time: 0.337s  
> Is my sort right: 1

可以可以，速度又提升了不少。

## 6、快速排序

在理解了基本算法思想之后，竟然在实现上有了卡顿。另一篇博客对于如何将大小数据进行挪动，有很形象的gif图说明。

主要的实现卡点为递归处，对于递归的理解，依然不到位。不不不！！！对于将数字进行左右分区的实现，也是不对的。

快速排序的基本规则为，和归并排序一样，是分治法的应用。

  1. 选一个数，使用这个数字，将整个待排序数列分成两部分，比这个数字小的放到左边，比这个数字大的数字放到右边。
  2. 从左边部分中再选一个数字，将左边部分分成两部分；对右边部分执行相同操作。
  3. 结束条件为，拆到最后没得拆了。如比3小的2和1是为左边部分，以2为拆分点，将比2小的1放到2的位置上，往右移，到结尾，将2放在最右边（即1）的位置上。



快速排序断断续续，分了3个时间段，各个时间段差不多花1小时，直到2020-6-29将它写出来，整个代码都算是抄的。遇到的那些问题，其实都是我的实现有问题。
    
    
    void MySort::quick(vector<int>& input, int left, int right) {  
     if (left < right) {  
      int middle = oneQuick(input, left, right);  
      quick(input, left, middle - 1);  
      quick(input, middle + 1, right);  
     }  
    }  
      
    int MySort::oneQuick(vector<int>& input, int left, int right) {  
     int pivot = input[left];  
      
     while (left < right) {  
      while (left < right && input[right] >= pivot) {  
       right--;  
      }  
      if (left < right) {  
       input[left] = input[right];  
       left += 1;  
      }  
      
      while (left < right && input[left] <= pivot) {  
       left++;  
      }  
      if (left < right) {  
       input[right] = input[left];  
       right -= 1;  
      }  
     }  
     input[left] = pivot;  
      
     return left;  
    }  
    

执行用时：

> STL use time: 0.018s  
> Bubble use time: 0.007s  
> Is my sort right: 1

竟然比STL的还快！真的是快速排序了。

换回原来的电脑后，执行用时有了变化：

> STL use time: 0.014s  
> Bubble use time: 0.051s  
> Is my sort right: 1

## 7、堆排序

懂得堆排序的大体框架，对于递归，我还是不甚理解。

由堆的性质决定，堆是一棵二叉树，且父节点必定大于（或小于）子节点的值，存放在一个数组中。当构建堆成功后，第一个元素则肯定为最大（最小）值。

构建堆后，将最大值放在最后一个位置，重新对堆进行处理，再将最大值放在倒数第二个位置。直到整个堆进行了调整。
    
    
    void MySort::adjustHeap(vector<int>& input, int size, int index) {  
     int left = index * 2 + 1;  
     int right = index * 2 + 2;  
     int largest = index;  
      
     if (left <= size - 1 && input[left] > input[largest]) {  
      largest = left;  
     }  
     if (right <= size - 1 && input[right] > input[largest]) {  
      largest = right;  
     }  
     if (largest == index) {  
      return;  
     }  
     else {  
      swap(input[largest], input[index]);  
      adjustHeap(input, size, largest);  
     }  
    }  
      
    void MySort::createHeap(vector<int>& input, int index) {  
     for (int i = (index - 1) / 2; i >= 0; --i) {  
      adjustHeap(input, index, i);  
     }  
    }  
      
    void MySort::heap(vector<int>& input) {  
     createHeap(input, input.size());  
      
      for (int i = input.size(); i > 0; --i) {  
       swap(input[0], input[i - 1]);  
      adjustHeap(input, i - 1, 0);  
      }  
    }  
    

执行用时，还是挺快的。比归并快些，比快排慢。

> STL use time: 0.013s  
> Bubble use time: 0.135s  
> Is my sort right: 1

至此，比较类排序全部搞完。

## 8、计数排序

在知道数字区间的时候，可以通过一个额外的数组，将每个数字出现的次数保存下来，然后再根据数字大小进行循环，将数字重新写入输入数组中。

我的实现版本：
    
    
    #include <unordered_map>  
      
    void MySort::counting(vector<int>& input) {  
     unordered_map<int, int> tmp;  
     unordered_map<int, int>::iterator iter;  
      
     for (size_t i = 0; i < input.size(); ++i) {  
      iter = tmp.find(input[i]);  
      if (iter != tmp.end()) {  
       iter->second += 1;  
      }  
      else {  
       tmp[input[i]] = 1;  
      }  
     }  
      
     size_t index = 0;  
     for (int i = -100000; i < 100000; ++i) {  
      iter = tmp.find(i);  
      if (iter != tmp.end()) {  
       for (int j = 0; j < iter->second; ++j) {  
        input[index] = iter->first;  
        ++index;  
       }  
      }  
      if (index == input.size()) {  
       break;  
      }  
     }  
    }  
    

执行用时：

> STL use time: 0.014s  
> Bubble use time: 0.916s  
> Is my sort right: 1

感觉应该是实现有问题吧。怎么会这么慢？对的，实现有问题，优化一把，不用unordered_map的版本。
    
    
    #include <string.h>  
      
    void MySort::counting(vector<int>& input) {  
     int* tmpArr = new int[200000];  
     if (tmpArr == NULL) {  
      return;  
     }  
     else {  
      memset(tmpArr, 0, sizeof(int) * 200000);  
     }  
      
     for (size_t i = 0; i < input.size(); ++i) {  
      int* val = tmpArr + input[i] + 100000;  
      (*val)++;  
     }  
      
     size_t index = 0;  
     for (int i = -100000; i < 100000; ++i) {  
      int count = *(tmpArr + i + 100000);  
      while (count > 0) {  
       input[index] = i;  
       index++;  
       count--;  
      }  
      if (index >= input.size()) {  
       break;  
      }  
     }  
      
     delete[] tmpArr;  
    }  
    

速度快了些。不止快了些，比快速排序还快了呢。

> STL use time: 0.013s  
> Bubble use time: 0.029s  
> Is my sort right: 1

## 9、引用链接

  1. 那篇超级厉害的博客：https://www.cnblogs.com/onepixel/p/7674659.html
  2. 维基百科希尔排序：https://zh.wikipedia.org/wiki/%E5%B8%8C%E5%B0%94%E6%8E%92%E5%BA%8F
  3. 分治法的介绍：https://blog.csdn.net/lemon_tree12138/article/details/48783535
  4. 快速排序的介绍：https://zhuanlan.zhihu.com/p/93129029 <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247485111&amp;idx=2&amp;sn=7730e7806b5a75426a0dc8b14b03be71&amp;chksm=a6c76a5a91b0e34c0d64cc9bc9415bc19a16e6ce802d610f73f3fdbdafc19b8a1e59b9bc3f0c" rel="noopener noreferrer">原文链接</a>）</small>