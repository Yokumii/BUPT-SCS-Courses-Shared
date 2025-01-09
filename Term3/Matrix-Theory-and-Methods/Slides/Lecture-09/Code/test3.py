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
        
def spectral_radius(A):
    '''
    矩阵谱半径
    小于等于所有矩阵范数
    '''   
    eigenvalues = np.linalg.eigvals(A)
    return np.max(np.abs(eigenvalues))

if __name__ == '__main__':
    #测试一下
    
    A = np.array([[0.1, 0.3],[0.7, 0.6]]) #课本例题
    A = np.array([[0.3174999, 0.39],[0.7, 0.6]]) #微调一下，使得谱半径接近于1
    B = Matrix(A)
    
    print('\n矩阵A的谱半径=')
    print('spectral radius:', spectral_radius(A))
    
    # =================================================================
    #可以验证，矩阵谱半径小于等于所有矩阵范数
    
    print('\n矩阵谱半径小于等于所有矩阵范数')
    
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
    #验证矩阵A是收敛矩阵
    
    k = int(1e2)
    print('\nA**k (k = 100) =\n', np.linalg.matrix_power(A,k))
    k = int(1e8)
    print('\nA**k (k = 1e8) =\n', np.linalg.matrix_power(A,k))
    k = 1000000000
    print('\nA**k (k->+oo) =\n', np.linalg.matrix_power(A,k))

    
    
    
    
    
    
    