# -*- coding: utf-8 -*-
'''
1 - 普通满秩分解
2 - 列主元满秩分解
'''

import numpy as np  
from scipy import linalg as la 


# N = 3000
# A = np.zeros([N,N])
# a0 = np.random.random([1,N])
# a1 = np.hstack((a0,a0))
# for k in range(0,N):
#     A[k,:] = a1[0, N-k:2*N-k]

A = np.array([[-1,0,1,2],[1,2,-1,1],[2,2,-2,-1]])
# A = np.array([[-1,0,1,2],[1,2,-1,1],[2,2,-2,-1],[2,2,-2,-1]])


#scipy版本plu分解, 列主元LU分解
P, L, U = la.lu(A) #A=PLU

'''
#补充, 取p为P的逆，就改成了通常所用的列主元LU分解  pA=LU
p = np.linalg.inv(P) #取p为P的逆, pA=LU
#'''


#pBC分解， 列主元满秩分解,  A = PBC

rank = np.linalg.matrix_rank(U)
B = L[:,0:rank]
C = U[0:rank,:]

print(np.linalg.norm(A - np.dot(P,np.dot(B,C)), 1))


from sympy import Matrix

L, U, _ = Matrix(A).LUdecomposition() # A = LU

#FG分解， 普通满秩分解,  A = FG
rank = U.rank()
F = L[:,0:rank]
G = U[0:rank,:]

print(np.linalg.norm(A - np.dot(F,G), 1))