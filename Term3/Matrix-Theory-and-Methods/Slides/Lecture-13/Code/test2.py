# -*- coding: utf-8 -*-
'''
qr分解 (下节课讲，这节课提前用到)

A = QR， 其中Q是酉矩阵，R是上三角矩阵

'''

import numpy as np  
from scipy import linalg as la 

N = 30
A = np.zeros([N,N])
a0 = np.random.random([1,N])
a1 = np.hstack((a0,a0))
for k in range(0,N):
    A[k,:] = a1[0, N-k:2*N-k]


#scipy版本QR分解
Q, R = la.qr(A) #A=QR

'''
A = QR,   Q:正交矩阵，  R:上三角矩阵
'''

print(np.linalg.norm(A - np.dot(Q,R), 1))

#判断Q为正交矩阵
print(np.linalg.norm(np.eye(N) - np.dot(Q,Q.transpose().conjugate()), 1))

#判断R是上三角矩阵，即对R进行LU分解，L是单位矩阵， U和R相等
from sympy import Matrix

L, U, _ = Matrix(R).LUdecomposition() #R=LU
print(np.linalg.norm(np.eye(N) - L, 1))
print(np.linalg.norm(U - R, 1))

