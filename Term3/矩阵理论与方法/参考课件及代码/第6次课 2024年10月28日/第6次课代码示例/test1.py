# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 10:43:23 2024

@author: lhc
"""

import numpy as np
import copy

# def gram_schmidt(basis): #施密特单位正交化
#     temp_vectors = copy.copy(basis)
#     Len = len(basis)
#     result = []
#     for k in range(Len):
#         # 当前处理的向量
#         current_vector = temp_vectors[k]
#         # 当前向量归一化
#         current_vector = current_vector / np.sqrt(inner_product(current_vector, current_vector))
#         # 从其他向量中移除当前向量的投影
#         for j in range(k+1, Len):
#             temp_vectors[j] = temp_vectors[j] - (inner_product(current_vector, temp_vectors[j])) * current_vector
#         # 添加正交化后的向量到结果中
#         result.append(current_vector)
#     return result

def gram_schmidt(basis): #施密特单位正交化(纯课本写法)
    x = copy.copy(basis)
    Len = len(basis)
    y = [x[0]]
    for m in range(0,Len-1): #正交化
        ym1 = x[m+1]
        for i in range(m+1):
            li = - inner_product(x[m+1],y[i])/inner_product(y[i],y[i])
            ym1 = ym1 + li * y[i]
        y.append(ym1)
    for m in range(0,Len): #单位化
        y[m] = y[m]/np.sqrt(inner_product(y[m],y[m]))
    return y
   
def inner_product(x, y): #定义内积
    return np.sum(x*y)

if __name__ == '__main__':
    # 课本P63 例1.33

    x1 = np.array([1,1,0,0])
    x2 = np.array([1,0,1,0])
    x3 = np.array([-1,0,0,1])
    x4 = np.array([1,-1,-1,1])

    basis = [x1,x2,x3,x4]
    orthonormal_basis = gram_schmidt(basis) #线性空间，内积空间

    print('课本P63 例1.33')
    print('标准正交基(e1,e2,e3,e4)=\n', orthonormal_basis) # 将一组基化为为标准正交基
