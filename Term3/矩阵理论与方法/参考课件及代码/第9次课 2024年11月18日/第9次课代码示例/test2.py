# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 10:43:23 2024

@author: lhc
"""
import numpy as np

def func_v1(x, n):
    '''
    vector = [1,x,x^2,...,x^n]
    '''
    vector = [1]
    for k in range(n):
        vector.append(vector[-1]*x)
    return vector

def gener_matrix_v1(n):
    '''
    这个例子体现了 y = a0 + a1*x + a1*x**2 + a1*x**3 +...+ a1*x**(n-1) + a1*x**n
    求系数a0,a1,...,an  中的一个过程
    XA=Y => A = inv(X) * Y
    中求矩阵X的逆，
    往往X的条件数很大，求逆困难（关键点不仅在函数，还在于x的取值，等分点条件数大，高斯点条件数小）
    '''
    X = []
    
    linspace_points = np.linspace(-1,1, n+1) # 等分点，导致X条件数大，尝试改为高斯点
    legendre_gauss_points = legendregauss(n+1, 0) #勒让德高斯点
    
    points_choice = linspace_points
    # points_choice = legendre_gauss_points #高斯点
    
    for k in range(n+1):
        x = points_choice[k]
        X.append(func_v1(x,n))
    X = np.array(X)
    return X
    
# ====================================================================

def legendre(n, m, x):
    '''求n次勒让德多项式函数的m次导数在x处的函数值'''
    if n == 0:
        if m >= 1:
            return 0
        else:
            return 1
    s = np.zeros([n + 1, m + 1])
    for j in range(0, m + 1):
        if j == 0:
            s[0, j] = 1
            s[1, j] = x
            for k in range(1, n):
                s[k + 1, j] = ((2 * k + 1) * x * s[k, j] - k * s[k - 1, j]) / (k + 1)
        else:
            s[0, j] = 0
            if j == 1:
                s[1, j] = 1
            else:
                s[1, j] = 0
            for k in range(1, n):
                s[k + 1, j] = (2 * k + 1) * s[k, j - 1] + s[k - 1, j]
    r = s[n, m]
    return r

def legendregauss(n, m):
    '''牛顿法求n次勒让德多项式m阶导数在区间[-1,1]中的所有零点，返回一个数组储存所有零点'''
    if n == 0:
        return []
    result = []
    error = 1e-8
    h = n**-2
    a = -1
    b = a + h
    for i in range(n - m):
        ya = legendre(n, m, a)
        yb = legendre(n, m, b)
        while(ya * yb > 0):
            a = b
            ya = yb
            b = a + h
            yb = legendre(n, m, b)
        x1 = (a + b)/2
        x0 = b
        while abs(x1 - x0) > error:
            x0 = x1
            x1 = x1 - legendre(n, m, x1) / legendre(n, m+1, x1)
        result.append(x1)
        a = x1 + h
        b = a + h
    return np.array(result)

def func_v2(x, n):
    '''
    vector = [P0,P1,P2,...,Pn]
    '''
    # 计算效率低，但好理解
    # vector = []
    # for k in range(n+1):
    #     vector.append(legendre(k, 0, x))

    #用秦九韶算法减少计算量
    vector = [1, x]
    for k in range(1,n):
        vector.append(((2 * k + 1) * x * vector[-1] - k * vector[-2]) / (k + 1))
    return vector

def gener_matrix_v2(n):
    '''
    这个例子体现了 y = a0*P0 + a1*P1 + a1*P2 + a1*P3 +...+ a1*P(n-1) + a1*Pn
    求系数a0,a1,...,an  中的一个过程
    PA=Y => A = inv(P) * Y
    中求矩阵P的逆，(实际工程中不是直接求逆，而是进一步用快速算法)
    往往P的条件数较小，求逆容易 （关键点不仅在函数，还在于x的取值，等分点条件数大，高斯点条件数小）
    
    P0,P1,P2,...   是勒让德多项式函数，  是正交多项式，满足(Pi,Pj) = delta(i,j)
    未来数值分析，计算方法，工程计算等课程会学：多项式插值
    '''
    P = []
    linspace_points = np.linspace(-1,1, n+1) # 等分点，导致X条件数大，尝试改为高斯点
    legendre_gauss_points = legendregauss(n+1, 0) #勒让德高斯点（关键点不仅在函数，还在于x的取值，等分点条件数大，高斯点条件数小）
    
    points_choice = linspace_points   #注意，若改成等分点，P矩阵依然病态
    points_choice = legendre_gauss_points #可以把这行注释掉， 看看等分点的效果
    
    for k in range(n+1):
        x = points_choice[k]
        P.append(func_v2(x,n))
    P = np.array(P)
    return P
    
if __name__ == '__main__':
    #测试一下
    #例1, 条件数大，求逆困难
    n = 50
    X = gener_matrix_v1(n)
    
    condition_number = np.linalg.cond(X)
    print('X condition_number = ', condition_number)
    invX = np.linalg.inv(X)
    print('||X*invX - I|| = ', np.linalg.norm(np.dot(X, invX) - np.eye(n+1)))
    # ========================================================================
    #例2, 条件数小，求逆容易,
    n = 50
    P = gener_matrix_v2(n)
    
    condition_number = np.linalg.cond(P)
    print('\nP condition_number = ', condition_number)
    invP = np.linalg.inv(P)
    print('||P*invP - I|| = ', np.linalg.norm(np.dot(P, invP) - np.eye(n+1)))
    
    
    
    
    
    
    
    