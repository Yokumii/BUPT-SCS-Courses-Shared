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

# ============================================================================================

pinvA = np.linalg.pinv(A)

# ============================================================================================

def my_pinv1(A):
    '''
    A = U D V^H, 
    SingularValue 为奇异值
    
    pinvA = V D_inv U^H
    '''
    
    U, SingularValue, V_H = la.svd(A) 

    m, n = A.shape
    
    D_inv = np.zeros((m, n)) + complex(0,0)
    for i in range(min(m, n)):
        D_inv[i,i] = 1/SingularValue[i]
    
    pinvA = np.dot(V_H.transpose().conjugate(), np.dot(D_inv, U.transpose().conjugate()))
    
    return pinvA


my_pinv1A = my_pinv1(A)

print(np.linalg.norm(pinvA - my_pinv1A, 1))

# ============================================================================================



def my_pinv2(A):
    '''
    A = U1 sigma V1^H, 
    SingularValue 为奇异值
    
    pinvA = V1 sigma^-1 U1^H
    '''
    
    B = np.dot(A.transpose().conjugate(), A)
        
    Lambda, V0 = np.linalg.eig(B)
    
    Lambda = np.abs(Lambda)
    
    V, R = la.qr(V0)
    
    rank = np.linalg.matrix_rank(A)
    
    D = A * complex(0,0)
    
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
    
    pinvA = np.dot(V1, np.dot(sigma_inv, U1.transpose().conjugate()))
    
    return pinvA

my_pinv2A = my_pinv2(A)

print(np.linalg.norm(pinvA - my_pinv2A, 1))




# ============================================================================================



def my_pinv3(A):
    '''
    A = PBC 列主元满秩分解
    
    pinvA = C^H (C C^H)^-1 (B^H B)^-1 B^H P^-1
    '''
    
    from scipy import linalg as la 
    
    #scipy版本plu分解, 列主元LU分解
    P, L, U = la.lu(A) #A=PLU
    
    rank = np.linalg.matrix_rank(U)
    B = L[:,0:rank]
    C = U[0:rank,:]
    
    # A= PBC
    
    pinvA = C.transpose().conjugate()
    pinvA = np.dot(pinvA, np.linalg.inv(np.dot(C, C.transpose().conjugate())))
    pinvA = np.dot(pinvA, np.linalg.inv(np.dot(B.transpose().conjugate(), B)))
    pinvA = np.dot(pinvA, B.transpose().conjugate())
    pinvA = np.dot(pinvA, np.linalg.inv(P))
    
    return pinvA

my_pinv3A = my_pinv3(A)

print(np.linalg.norm(pinvA - my_pinv3A, 1))



# ============================================================================================




m = int(N/20) + 1
n = int(N/30) + 1
A = A[0:m,0:n] #取矩阵小一点，满秩分解也快一些
A = abs(A)



pinvA = np.linalg.pinv(A)


def my_pinv4(A):
    '''
    A = BC 普通满秩分解 (不推荐)
    
    pinvA = C^H (C C^H)^-1 (B^H B)^-1 B^H
    '''
    
    from sympy import Matrix
    
    L, U, _ = Matrix(A).LUdecomposition() # A = LU
    rank = U.rank()
    B = L[:,0:rank]
    C = U[0:rank,:]
    
    # A= BC
    
    pinvA = C.transpose().conjugate()
    pinvA = np.dot(pinvA, np.linalg.inv(np.double(np.dot(C, C.transpose().conjugate()))))
    pinvA = np.dot(pinvA, np.linalg.inv(np.double(np.dot(B.transpose().conjugate(), B))))
    pinvA = np.dot(pinvA, B.transpose().conjugate())
    
    return pinvA

my_pinv4A = my_pinv4(A)

print(np.linalg.norm(pinvA - my_pinv4A, 1))



