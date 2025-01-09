# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 10:43:23 2024

@author: lhc
"""


import numpy as np
from sympy import Matrix
   
# 课本P49 例1.26
A = np.array([[-1,1,0],[-4,3,0],[1,0,2]])
A = Matrix(A)
P, J = A.jordan_form() #A = PJ(P^-1)
invP = P.inv()
    
print('课本P49 例1.26 A=PJP^-1')
print('A=\n',np.array(A))
print('\nP=\n',np.array(P),'\nJ=\n',np.array(J),'\nP^-1=\n',np.array(invP))
print('\n||A-PJP^-1||=',(A - P*J*invP).norm()) #A = PJ(P^-1)
    
print('\n=====================================================\n')
    
# 课本P49 例1.27
A = np.array([[1,2,3,4],[0,1,2,3],[0,0,1,2],[0,0,0,1]])
A = Matrix(A)
P, J = A.jordan_form() #A = PJ(P^-1)
invP = P.inv()
    
print('课本P49 例1.27 A=PJP^-1')
print('A=\n',np.array(A))
print('\nP=\n',np.array(P),'\nJ=\n',np.array(J),'\nP^-1=\n',np.array(invP))
print('\n||A-PJP^-1||=',(A - P*J*invP).norm()) #A = PJ(P^-1)
    
        

print('\n=====================================================\n')
    
# 课本P56 第19题(2)
# A = np.array([[3,1,0,0],[-4,-1,0, 0],[7,1,2,1],[-7,-6,-1,0]])
        
        
    
