# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 10:43:23 2024

@author: lhc
"""
import numpy as np

def column_vector_norm(x, p = 2):
    '''
    列向量的lp范数, p >= 1
    '''
    if p == np.Inf: #无穷范数
        return np.max(np.abs(x))
    return np.sum(np.abs(x)**p)**(1/p) #lp范数, p >= 1
    
if __name__ == '__main__':
    #测试一下
    
    x = np.array([[1],[2],[-3]])
    print('列向量x=\n',x)
    
    p = np.Inf
    print('\n列向量x的无穷范数=')
    print('my_norm:',column_vector_norm(x, p))
    print('numpy_n:',np.linalg.norm(x, p))
        
    p = 1
    print('\n列向量x的l1范数=')
    print('my_norm:',column_vector_norm(x, p))
    print('numpy_n:',np.linalg.norm(x, p))
    
    p = 2
    print('\n列向量x的l2范数=')
    print('my_norm:',column_vector_norm(x, p))
    print('numpy_n:',np.linalg.norm(x, p))
    
    p = 3
    print('\n列向量x的l3范数=')
    print('my_norm:',column_vector_norm(x, p))
    print('numpy_n:',np.linalg.norm(x, p))  #可能会报错, 注释掉就行
    
    
    