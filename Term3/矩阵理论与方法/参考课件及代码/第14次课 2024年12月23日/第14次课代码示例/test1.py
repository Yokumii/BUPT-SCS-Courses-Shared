# -*- coding: utf-8 -*-
'''
qr分解 

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

A = A + complex(0,1)

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



def my_qr(A):
    
    Len, _ = A.shape
    K = np.eye(Len) + complex(0,0)
    
    B = np.zeros((Len,Len)) + complex(0,0)
    Lambda = np.zeros((Len,Len))
    Lambda_2 = np.zeros((Len,Len))
    
    Q = np.zeros((Len,Len)) + complex(0,0)
    
    for k in range(0, Len):
        B[:,k] = A[:,k]
        for j in range(0, k):
            K[j,k] = np.sum(B[:,j].conjugate() * A[:,k])/Lambda_2[j,j]
            B[:,k] = B[:,k] - K[j,k] * B[:,j]
        
        Lambda_2[k,k] = np.sum(abs(B[:,k])**2)
        Lambda[k,k] = np.sqrt(Lambda_2[k,k])
        Q[:,k] = B[:,k] / Lambda[k,k]
    
    R = np.dot(Lambda,K)
    
    return Q,R


q,r = my_qr(A)

print(np.linalg.norm(A - np.dot(q,r), 1))
print(np.linalg.norm(np.eye(N) - np.dot(q,q.transpose().conjugate()), 1))

L, U, _ = Matrix(r).LUdecomposition() #R=LU
print(np.linalg.norm(np.eye(N) - L, 1))
print(np.linalg.norm(U - r, 1))