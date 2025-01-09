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



class linear_transformation(object):
    
    def __init__(self, linear_space, transformation):
        self.linear_space = linear_space #线性空间
        self.trans = transformation #变换
        self.trans2matrix() #线性变换在标准正交基下的矩阵
        
    def trans2matrix(self): #线性变换在标准正交基下的矩阵
        te = []
        for line in self.linear_space.basis:
            te.append(self.trans(line))
        Len = self.linear_space.dim()
        self.matrix = np.zeros([Len,Len])
        for j in range(0, Len):
            for k in range(0, Len):
                self.matrix[k,j] = self.linear_space.inner_product(te[j], self.linear_space.basis[k])
        
        self.matrix = Matrix(self.matrix)
        P, J = self.matrix.jordan_form() #self.matrix = PJ(P^-1)
        invP = P.inv()
        self.P = P
        self.J = J
        self.invP = invP
        # print((self.matrix - P*J*invP).norm()) #self.matrix = PJ(P^-1)        
        
        
    def linear_trans(self, input_ele): #利用矩阵相乘来计算坐标
        output_ele = copy.copy(input_ele)
        # output_ele.coordinate = np.dot(self.matrix, input_ele.coordinate) #直接乘矩阵
        output_ele.coordinate = np.dot(self.P*self.J*self.invP, input_ele.coordinate) #利用jordan标准形
        return output_ele

    def dot(self, arr): #矩阵相乘
        y = np.dot(self.matrix, arr) 
        return y

    def dotJ(self, arr): #矩阵相乘
        y = np.dot(self.J, arr) 
        return y
    
    def apply_function(self, func): #将线性变换的函数作用于基本线性变换中，并且修改矩阵
        # self.matrix = func(self.dot)(np.eye(self.linear_space.dim())) #直接计算，满矩阵相乘
        
        self.J = func(self.dotJ)(np.eye(self.linear_space.dim())) #基于f(T) 计算f(J)，更新为J
        self.matrix = self.P*self.J*self.invP #更新矩阵
        self.trans = func(self.trans)
        
        
#########################################################################

def basis_coordinate(x, basis):
    '''
    通过坐标变换求元素x在其他基(X1,X2,X3)下的坐标beta
    首先有x = (e1,e2,e3) alpha #(e1,e2,e3)为线性空间V的标准正交基，alpha 为x在该基下的坐标
    先求过渡矩阵C：(X1,X2,X3) = (e1,e2,e3)C
    有 (e1,e2,e3) = (X1,X2,X3) C^-1, 带入上上式
    得 x = (X1,X2,X3) C^-1 *alpha
    得 beta = C^-1 *alpha
    满足 x = (X1,X2,X3) C^-1 * beta
    
    仅示意，实际使用要具体情况具体再写，不要直接调用本函数，否则每次都会重新计算过渡矩阵和逆，造成冗余。
    应该提前把过渡矩阵和逆计算好再保存，然后每次求坐标的时候进行调用即可
    '''
    alpha = x.coordinate #线性变换在标准正交基(e1,e2,e3)下的矩阵A已经提前算好了
    ls = x.linear_space #线性空间
    C = []
    Len = len(basis) #等于T.linear_space.dim()
    for j in range(0, Len):
        xj = element(ls, 'value', basis[j]) 
        C.append(xj.coordinate) #求Xj 在标准正交基下的坐标
    C = np.array(C).transpose() #把坐标合并成矩阵，过渡矩阵，满足(X1,X2,X3) = (e1,e2,e3)C, 注意转置
    invC = np.linalg.inv(C) #求C的逆C^-1
    beta = np.dot(invC, alpha) #B = C^-1 *A*C
    return beta


def trans_basis_matrix(T, basis):
    '''
    通过坐标变换求线性变换在其他基(X1,X2,X3)下的矩阵
    由 T(e1,e2,e3) = (e1,e2,e3)A #(e1,e2,e3)为线性空间V的标准正交基
    先求过渡矩阵C：(X1,X2,X3) = (e1,e2,e3)C
    有 (e1,e2,e3) = (X1,X2,X3) C^-1, 带入上上式
    得T(X1,X2,X3) C^-1 = (X1,X2,X3) C^-1 *A
    即T(X1,X2,X3)  = (X1,X2,X3) C^-1 *A*C
    得 B = C^-1 *A*C
    满足 T(X1,X2,X3) = (X1,X2,X3)B
    '''
    A = T.matrix #线性变换在标准正交基(e1,e2,e3)下的矩阵A已经提前算好了
    C = []
    Len = len(basis) #等于T.linear_space.dim()
    for j in range(0, Len):
        xj = element(ls, 'value', basis[j]) 
        C.append(xj.coordinate) #求Xj 在标准正交基下的坐标
    C = np.array(C).transpose() #把坐标合并成矩阵，过渡矩阵，满足(X1,X2,X3) = (e1,e2,e3)C, 注意转置
    invC = np.linalg.inv(C) #求C的逆C^-1
    B = np.dot(invC, np.dot(A,C)) #B = C^-1 *A*C
    return B

#########################################################################

def mapping(x): #基本的线性变换
    y = x + np.transpose(x)
    return y

def function(T): #线性变换的函数
    def inner_function(x):
        basis = [x] #快速算法, 求多项式基（仿秦九韶算法）
        N = 1
        for n in range(0,N):
            basis.append(T(basis[-1]))
        
        number_field = float #实数域
        ls = linear_space(basis, number_field) #线性变换的幂张成一个线性空间
        alpha = [0, 1]
        a = element(ls, 'coordinate', alpha)
        y = a.value()
        return y
    return inner_function

def inner_product(x, y): #定义内积
    return np.sum(x*y)


if __name__ == '__main__':
    # 问题c：1-求标准正交基；2-求元素在标准正交基下的坐标

    basis = [np.array([[-1,1],[0,0]]), np.array([[-1,0],[1,0]]), np.array([[0,0],[0,1]])]
    
    number_field = float #实数域
    
    ls = inner_product_space(basis, number_field, inner_product) #线性空间，内积空间
    print('线性空间的一组标准正交基(e1,e2,e3)=\n',ls.basis) # 自动修改线性空间中的基为标准正交基
    
    x = np.array([[4,-4],[0,-3]])
    print('x=\n',x)
    
    x_ele = element(ls, 'value', x)  #给定x，求x在标准正交基下的坐标
    print('x在标准正交基下的坐标:\n',x_ele.coordinate) #该元素在标准正交基下求坐标
    
    x_ele2 = element(ls, 'coordinate', x_ele.coordinate)  #直接给坐标来生成
    print('检验x=\n',x_ele2.value()) #检验一下
    
    #########################################################################
    # 通过坐标变换求元素在其他基下的坐标
    
    basis_X = [np.array([[-1,1],[0,0]]), np.array([[-1,0],[1,0]]), np.array([[0,0],[0,1]])]
    coordinate_X = basis_coordinate(x_ele, basis_X) #求x_ele在基(X1,X2,X3)下的坐标
    print('\n求x_ele在基(X1,X2,X3)下的坐标beta=\n',coordinate_X)
    ls_X = linear_space(basis_X, number_field) #线性空间
    x_X = element(ls_X, 'coordinate', coordinate_X)
    print('||x - (X1,X2,X3)beta||=', np.linalg.norm(x_X.value()-x)) #检验坐标是否计算正确
    
    
    basis_Y = [np.array([[1,1],[-2,0]]), np.array([[-1,0],[1,1]]), np.array([[-1,0],[1,-1]])]
    coordinate_Y = basis_coordinate(x_ele, basis_Y) #求x_ele在基(Y1,Y2,Y3)下的坐标
    print('\n求x_ele在基(Y1,Y2,Y3)下的坐标beta=\n',coordinate_Y)
    ls_Y = linear_space(basis_Y, number_field) #线性空间
    x_Y = element(ls_Y, 'coordinate', coordinate_Y)
    print('||x - (Y1,Y2,Y3)beta||=', np.linalg.norm(x_Y.value()-x)) #检验坐标是否计算正确
    
    
    print('============以上是求坐标==============')
    print('=====================================')
    print('============以下是求矩阵==============')
    #########################################################################
    # 求线性变换在标准正交基下的矩阵
    
    lt = linear_transformation(ls, mapping) #基本的线性变换
    
    flt = copy.copy(lt)
    flt.apply_function(function)   #线性变换的函数，也是线性变换
    
    print('\n 线性变换在标准正交基下的矩阵A=\n',flt.matrix) #线性变换在标准正交基下的矩阵
    print('满足T(e1,e2,e3) = (e1,e2,e3)A\n')
    #########################################################################
    # 通过坐标变换求线性变换在其他基下的矩阵
    
    basis_X = [np.array([[-1,1],[0,0]]), np.array([[-1,0],[1,0]]), np.array([[0,0],[0,1]])]
    B = trans_basis_matrix(flt, basis_X) #通过坐标变换求线性变换在其他基下的矩阵
    print('线性变换flt在基(X1,X2,X3)下的矩阵B=\n',B)
    print('满足T(X1,X2,X3) = (X1,X2,X3)B\n')
    
    
    basis_Y = [np.array([[1,1],[-2,0]]), np.array([[-1,0],[1,1]]), np.array([[-1,0],[1,-1]])]
    B = trans_basis_matrix(flt, basis_Y) #通过坐标变换求线性变换在其他基下的矩阵
    print('线性变换flt在基(Y1,Y2,Y3)下的矩阵B=\n',B)
    print('满足T(Y1,Y2,Y3) = (Y1,Y2,Y3)B\n')
    
    # 第3次课第2个ppt第18页的例子
    basis_Z = [np.array([[0,1],[-1,0]]), np.array([[-2,1],[1,0]]), np.array([[0,0],[0,1]])]
    B = trans_basis_matrix(flt, basis_Z) #通过坐标变换求线性变换在其他基下的矩阵
    print('线性变换flt在基(Z1,Z2,Z3)下的矩阵B=\n',B)
    print('满足T(Z1,Z2,Z3) = (Z1,Z2,Z3)B\n')
    
    
    
    
    
    
    
    
