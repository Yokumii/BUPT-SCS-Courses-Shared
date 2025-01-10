# -*- coding: utf-8 -*-
'''
svd分解
'''

import numpy as np  
from scipy import linalg as la 


N = 500
A = np.zeros([N,N])
a0 = np.random.random([1,N])
a1 = np.hstack((a0,a0))
for k in range(0,N):
    A[k,:] = a1[0, N-k:2*N-k]

A = A +complex(0,1)
# A = np.array([[-1,0,1,2],[1,2,-1,1],[2,2,-2,-1]])
# A = np.array([[-1,0,1,2],[1,2,-1,1],[2,2,-2,-1],[2,2,-2,-1]])


def my_svd(A):
    '''
    A = U D V^H, 
    SingularValue 为奇异值
    '''
    U, SingularValue, V_H = la.svd(A) 
    m, n = A.shape
    
    D = np.zeros((m, n)) + complex(0,0)
    for i in range(min(m, n)):
        D[i,i] = SingularValue[i]
    
    V = V_H.transpose().conjugate()
    return U, D, V,  SingularValue

U, D, V, SingularValue = my_svd(A)

print(np.linalg.norm(A - np.dot(np.dot(U,D), V.transpose().conjugate()), 1))
# print(np.linalg.norm(np.eye(U.shape[0]) - np.dot(U, U.transpose().conjugate()), 1))
# print(np.linalg.norm(np.eye(V.shape[0]) - np.dot(V, V.transpose().conjugate()), 1))


# ============================================================================================

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

def my_svd2(A):
    '''
    A = U D V^H, 
    SingularValue 为奇异值
    '''
    
    B = np.dot(A.transpose().conjugate(), A)
        
    Lambda, V0 = np.linalg.eig(B)
    
    Lambda = np.abs(Lambda)
    
    V, R = la.qr(V0)
    
    rank = np.linalg.matrix_rank(A)
    
    D = A *   complex(0,0)
    
    sigma = np.zeros((rank,rank))  + complex(0,0)
    sigma_inv = np.zeros((rank,rank))  + complex(0,0)
    SingularValue = []
    
    for i in range(0,rank):
        D[i,i] = np.sqrt(Lambda[i])
        sigma[i,i] = D[i,i]
        sigma_inv[i,i] = 1 / sigma[i,i]
        SingularValue.append(D[i,i]) 
    
    V1 = V[:,0:rank]
    U1 = np.dot(np.dot(A,V1), sigma_inv)
    
    U = A1_to_A(U1)
    
    SingularValue = np.array(SingularValue)
    
    return U, D, V,  SingularValue


U, D, V, SingularValue = my_svd2(A)

print(np.linalg.norm(A - np.dot(np.dot(U,D), V.transpose().conjugate()), 1))












