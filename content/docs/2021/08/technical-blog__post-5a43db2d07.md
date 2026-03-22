---
title: pyc文件的初步认识
date: '2021-08-08'
weight: 289990005
primary_category: technical-blog
source_url: http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484225&idx=2&sn=244c95acbdaddf32176b8b5a4630d42d&chksm=a6c76fac91b0e6ba00b2cffce35cb6e8a1ac7da83fa7a607d52b25167fe3a89d8aa9385128ac
---
搞清楚字节码被dis展示内容的各个位置含义后，下一步，是搞清楚pyc文件是什么。pyc文件是什么呢？它是Python存储字节码的地方，可以很方便的借助marshal模块看它的内容。

先来一个很简单的Python文件，试验一番。
    
    
    # simple.py  
    print('Hello world')  
    

用以下指令生成对应的pyc（如果这个py文件被import，那么也会生成对应的pyc文件）。
    
    
    py -3 -m compileall simple.py  
    

接着，可以用以下脚本，看到其中code_obj，通过dis出来的结果，与此前的试验结果一样了。
    
    
    # test_marshal.py  
    import marshal, sys, dis  
      
    header_size = 8  
    if sys.version_info >= (3, 6):  
    	header_size = 16  
    if sys.version_info >= (3, 7):  
    	header_size = 16  
      
      
    with open('__pycache__/simple.cpython-39.pyc', 'rb') as f:  
    	# 文件的头部长度，因Python版本差异有所不同  
    	metadata = f.read(header_size)  
    	print(f'header is: {metadata, len(metadata)}')  
      
    	# 可以直接使用marshal模块将pyc文件load出来  
    	code_obj = marshal.load(f)  
    	dis.dis(code_obj)  
    

我去看了一下Python中的源码，与上面函数是类似的，也是分为两块，忽略掉头部内容，其后便是字节码了。
    
    
    // Python/pythonrun.c  
    static PyObject *  
    run_pyc_file(FILE *fp, const char *filename, PyObject *globals,  
                 PyObject *locals, PyCompilerFlags *flags)  
    {  
        PyThreadState *tstate = _PyThreadState_GET();  
        PyCodeObject *co;  
        PyObject *v;  
        long magic;  
        long PyImport_GetMagicNumber(void);  
      
        magic = PyMarshal_ReadLongFromFile(fp);  
        if (magic != PyImport_GetMagicNumber()) {  
            if (!PyErr_Occurred())  
                PyErr_SetString(PyExc_RuntimeError,  
                           "Bad magic number in .pyc file");  
            goto error;  
        }  
        /* Skip the rest of the header. */  
        (void) PyMarshal_ReadLongFromFile(fp);  
        (void) PyMarshal_ReadLongFromFile(fp);  
        (void) PyMarshal_ReadLongFromFile(fp);  
        if (PyErr_Occurred()) {  
            goto error;  
        }  
        v = PyMarshal_ReadLastObjectFromFile(fp);  
        if (v == NULL || !PyCode_Check(v)) {  
            Py_XDECREF(v);  
            PyErr_SetString(PyExc_RuntimeError,  
                       "Bad code object in .pyc file");  
            goto error;  
        }  
        fclose(fp);  
        co = (PyCodeObject *)v;  
        v = run_eval_code_obj(tstate, co, globals, locals);  
        if (v && flags)  
            flags->cf_flags |= (co->co_flags & PyCF_MASK);  
        Py_DECREF(co);  
        return v;  
    error:  
        fclose(fp);  
        return NULL;  
    }  
    

在网上搜了一下pyc文件的好处，有以下两点：

  * 如果进行大量处理，使用pyc可节省编译时间；

  * 与py文件执行效果相同，可以藏起来源码。 <small>（<a href="http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&amp;mid=2247484225&amp;idx=2&amp;sn=244c95acbdaddf32176b8b5a4630d42d&amp;chksm=a6c76fac91b0e6ba00b2cffce35cb6e8a1ac7da83fa7a607d52b25167fe3a89d8aa9385128ac" rel="noopener noreferrer">原文链接</a>）</small>




  


* * *