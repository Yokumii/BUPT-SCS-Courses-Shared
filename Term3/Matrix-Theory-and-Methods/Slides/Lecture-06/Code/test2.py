# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 10:43:23 2024

@author: lhc
"""
import numpy as np
import copy
from sympy import Matrix
   
class linear_space(object):
    
    def __init__(self, basis = [], number_field = complex):
        self.basis = basis #基
        self.number_field = number_field #数域

    def dim(self):
        return(len(self.basis)) #维数
    
class inner_product_space(linear_space): #内积空间
    
    def __init__(self, basis = [], number_field = complex, inner_product= 'None'):
        linear_space.__init__(self, basis, number_field)
        self.inner_product = inner_product
        self.gram_schmidt()
        
    def gram_schmidt(self): #施密特单位正交化
        temp_vectors = copy.copy(self.basis)
        Len = self.dim()
        result = []
        for k in range(Len):
            # 当前处理的向量
            current_vector = temp_vectors[k]
            # 当前向量归一化
            current_vector = current_vector / np.sqrt(self.inner_product(current_vector, current_vector))
            # 从其他向量中移除当前向量的投影
            for j in range(k+1, Len):
                temp_vectors[j] = temp_vectors[j] - (self.inner_product(current_vector, temp_vectors[j])) * current_vector
            # 添加正交化后的向量到结果中
            result.append(current_vector)
        self.basis = result
   
def inner_product(x, y): #定义内积
    return np.sum(x*y)

class element(object):
    
    def __init__(self, linear_space, info = 'coordinate', infomation = []):
        self.linear_space = linear_space #线性空间
        if info == 'coordinate':
            self.list2coordinate(infomation) #坐标
        if info == 'value':
            self.value2coordinate(infomation) #值
            
    def list2coordinate(self, coordinate):
        self.coordinate = []
        for line in coordinate:
            self.coordinate.append(self.linear_space.number_field(line))
        self.coordinate = np.array(self.coordinate)
 
    def value2coordinate(self, value): #计算坐标
        Len = self.linear_space.dim()
        self.coordinate = []
        for k in range(0, Len):
            self.coordinate.append(self.linear_space.inner_product(value, self.linear_space.basis[k]))
        self.coordinate = np.array(self.coordinate)
    
    def value(self): #计算数值
        v = self.linear_space.basis[0] * self.coordinate[0]
        Len = self.linear_space.dim()
        for k in range(1, Len):
            v = v + self.linear_space.basis[k] * self.coordinate[k]
        return v

if __name__ == '__main__':
    # 课本P63 例1.33

    x1 = np.array([1,1,0,0])
    x2 = np.array([1,0,1,0])
    x3 = np.array([-1,0,0,1])
    x4 = np.array([1,-1,-1,1])

    basis = [x1,x2,x3,x4]
    
    number_field = float #实数域
    
    ls = inner_product_space(basis, number_field, inner_product) #线性空间，内积空间

    print('课本P63 例1.33')
    print('线性空间的一组标准正交基(e1,e2,e3,e4)=\n',ls.basis) # 自动修改线性空间中的基为标准正交基
    
