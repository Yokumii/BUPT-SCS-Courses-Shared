# -*- coding: utf-8 -*-
'''
利用qr分解，求svd分解中最后一步：把u1扩充成酉矩阵
'''

import numpy as np  
from scipy import linalg as la 

def gener_A1(N = 500):
    
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
    
    M = N//5+1
    
    A1 = Q[:,0:M]
    # A1 = Q
    return A1


def A1_to_A(A1):
    
    N,n = A1.shape
    A0 = np.zeros((N,N)) + complex(0,0)
       
    A0[:,0:n] = A1[:,:]
       
    P, L, U = la.lu(A0)
       
       
    B = np.eye(N) * 1
    B[:,0:n] = 0
    U = U + B
       
    AA = np.dot(P, np.dot(L, U))
    Q, R = la.qr(AA)
       
    A = Q
    A[:,0:n] = A1[:,:]
    return A

A1 = gener_A1(1000)
N,n = A1.shape

A = A1_to_A(A1)


print(np.linalg.norm(np.eye(N) - np.dot(A,A.transpose()),1))
   
print(np.linalg.norm(A[:,0:n] - A1,1))   




