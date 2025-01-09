# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 10:43:23 2024

@author: lhc
"""
import numpy as np
from sympy import Matrix, oo

def matrix_norm(A, p = 2):
    '''
    矩阵范数
    课本90页，从属范数
    课本86页-87页-m范数，F范数
    '''
    if p == 1: #1范数, 列和范数
        return np.max(np.sum(np.abs(A),axis = 0))
    if p == 2: #2范数, 谱范数
        SingularValues = np.linalg.eigvals(np.dot(A.transpose().conjugate(),A))
        return np.sqrt(np.max(np.abs(SingularValues)))
    if p == np.Inf: #无穷范数, 行和范数
        return np.max(np.sum(np.abs(A),axis = 1))
    if p == 'm1':
        return np.sum(np.abs(A))
    if p == 'm2' or p == 'F':
        return np.sum(np.abs(A)**2)**(1/2)
    if p == 'moo':
        return np.max(np.abs(A)) * A.shape[1]
        
if __name__ == '__main__':
    #测试一下
    
    A = np.array([[complex(0,-1),2,3],[1,0,complex(0,1)]])
    B = Matrix(A)
    
    p = 1
    print('\n矩阵A的1范数=')
    print('my_norm:',matrix_norm(A, p))
    print('sympy_M:',Matrix.norm(B, p))
    print('numpy_n:',np.linalg.norm(A, p))
    
    p = 2
    print('\n矩阵A的2范数=')
    print('my_norm:',matrix_norm(A, p))
    print('sympy_M:',Matrix.norm(B, p))
    print('numpy_n:',np.linalg.norm(A, p))
    
    p = np.Inf
    print('\n矩阵A的无穷范数=')
    print('my_norm:',matrix_norm(A, p))
    print('sympy_M:',Matrix.norm(B, oo))
    print('numpy_n:',np.linalg.norm(A, p))
    
    
    p = 'm1'
    print('\n矩阵A的m1范数=')
    print('my_norm:',matrix_norm(A, p))
    
    p = 'm2'
    p = 'F'
    print('\n矩阵A的m2范数(也叫F范数)=')
    print('my_norm:',matrix_norm(A, p))
    
    p = 'moo'
    print('\n矩阵A的m无穷范数=')
    print('my_norm:',matrix_norm(A, p))
    
    # =============================================================================
    
    print('\n验证单位矩阵I = np.eye(10)的各个范数：')
    A = np.eye(10)
    B = Matrix(A)
    
    p = 1
    print('\n矩阵I的1范数=')
    print('my_norm:',matrix_norm(A, p))
    print('sympy_M:',Matrix.norm(B, p))
    print('numpy_n:',np.linalg.norm(A, p))
    
    p = 2
    print('\n矩阵I的2范数=')
    print('my_norm:',matrix_norm(A, p))
    print('sympy_M:',Matrix.norm(B, p))
    print('numpy_n:',np.linalg.norm(A, p))
    
    p = np.Inf
    print('\n矩阵I的无穷范数=')
    print('my_norm:',matrix_norm(A, p))
    print('sympy_M:',Matrix.norm(B, oo))
    print('numpy_n:',np.linalg.norm(A, p))
    
    
    p = 'm1'
    print('\n矩阵I的m1范数=')
    print('my_norm:',matrix_norm(A, p))
    
    p = 'm2'
    p = 'F'
    print('\n矩阵I的m2范数(也叫F范数)=')
    print('my_norm:',matrix_norm(A, p))
    
    p = 'moo'
    print('\n矩阵I的m无穷范数=')
    print('my_norm:',matrix_norm(A, p))
    
    
    