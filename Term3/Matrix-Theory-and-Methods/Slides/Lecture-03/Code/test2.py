# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 10:43:23 2024

@author: lhc
"""


import numpy as np
import copy
   
class linear_space(object):
    
    def __init__(self, basis = [], number_field = complex):
        self.basis = basis #基
        self.number_field = number_field #数域

    def dim(self):
        return(len(self.basis)) #维数
    
class element(object):
    
    def __init__(self, linear_space, info = 'coordinate', infomation = []):
        self.linear_space = linear_space #线性空间
        if info == 'coordinate':
            self.list2coordinate(infomation) #坐标
        if info == 'value':
            self.value2coordinate(infomation) #值
            
    def list2coordinate(self, coordinate):
        self.coordinate = np.array(coordinate)
 
    def value(self): #计算数值
        v = self.linear_space.basis[0] * self.coordinate[0]
        Len = self.linear_space.dim()
        for k in range(1, Len):
            v += self.linear_space.basis[k] * self.coordinate[k]
        return v

class linear_transformation(object):
    
    def __init__(self, linear_space, transformation, matrix):
        self.linear_space = linear_space #线性空间
        self.trans = transformation #变换
        self.trans2matrix(matrix) #线性变换在积下的矩阵
        
    def trans2matrix(self, matrix): #线性变换在积下的矩阵
        '''
        注：本来不是手动计算，而是自动计算
        后续课程会讲如何自动计算线性变换在基下的矩阵
        '''
        self.matrix = matrix
            
    def linear_trans(self, input_ele): #利用矩阵相乘来计算坐标
        output_ele = copy.copy(input_ele)
        output_ele.coordinate = np.dot(self.matrix, input_ele.coordinate)
        return output_ele

    def dotM(self, arr): #矩阵相乘
        y = np.dot(self.matrix, arr) 
        return y

    def apply_function(self, func): #将线性变换额函数作用于基本线性变换中，并且修改矩阵
        self.matrix = func(self.dotM)(np.eye(self.linear_space.dim()))
        self.trans = func(self.trans)
        
#########################################################################


def mapping(x): #基本的线性变换
    A = np.array([[0,1],[1,0]])
    y = np.dot(A, x) 
    return y

'''
def power_T(T,x): #线性变换的幂
    def inner_function(N):
        y = x
        for n in range(0,N):
            y = T(y)
        return y
    return inner_function

def function(T): #线性变换的函数
    def inner_function(x):
        P = power_T(T,x)
        # y = P(T,x)(3) + 2 * P(T,x)(1) #和下面的计算结果一样
        # y =  T(T(T(x))) + 2 * T(x) #和下面的计算结果一样
        basis = [P(0), P(1), P(2), P(3)] #线性变换的幂，作为一组基, 和下面的一样
        number_field = float #实数域
        ls = linear_space(basis, number_field) #线性变换的幂张成一个线性空间
        alpha = [0, 2, 0, 1]
        a = element(ls, 'coordinate', alpha)
        y = a.value()
        return y
    return inner_function
'''

def function(T): #线性变换的函数
    def inner_function(x):
        basis = [x] #快速算法, 求多项式基（仿秦九韶算法）
        N = 3
        for n in range(0,N):
            basis.append(T(basis[-1]))
        
        number_field = float #实数域
        ls = linear_space(basis, number_field) #线性变换的幂张成一个线性空间
        alpha = [0, 2, 0, 1]
        a = element(ls, 'coordinate', alpha)
        y = a.value()
        return y
    return inner_function


if __name__ == '__main__':
    #测试

    basis = [np.array([[1,0],[1,0]]), np.array([[0,1],[0,1]]), 
             np.array([[-1,0],[1,0]]), np.array([[0,-1],[0,1]])] #R^2*2上一组基
    
    number_field = float #实数域
    # number_field = complex #复数域
    
    ls = linear_space(basis, number_field) #线性空间
    
    x1, x2, x3, x4 = 1, 2, 3, 4
    x = np.array([[x1,x2],[x3,x4]]) 
    
    alpha = [0.5*(x1+x3), 0.5*(x2+x4), 0.5*(-x1+x3), 0.5*(-x2+x4)] #人工手动计算坐标
    
    a = element(ls, 'coordinate', alpha)  #直接给坐标来生成
    '''
    思考：如何实现：
    x = np.array([[x1,x2],[x3,x4]])
    x -> a 利用算法自动求x在基下的坐标？
    后续课程会讲
    '''
    #########################################################################
    
    b = function(mapping)(a.value()) #直接计算
    print('直接计算f(T)(x):\n',b)
    
    
    matrix = np.diag([1, 1, -1, -1]) #提前手动计算线性变换在基下的矩阵
    lt = linear_transformation(ls, mapping, matrix) #线性变换
    '''
    思考：如何实现：
    lt = linear_transformation(ls, mapping) 
    不输入矩阵，而是让算法自动计算？
    后续课程会讲
    '''
    
    flt = copy.copy(lt)
    flt.apply_function(function)   #线性变换的函数，也是线性变换
    
    c = flt.linear_trans(a)
    print('利用矩阵论框架计算f(T)(x):\n',c.value())
    