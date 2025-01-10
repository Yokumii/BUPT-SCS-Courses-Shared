# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 10:43:23 2024

@author: lhc
"""
import numpy as np
from sympy import Matrix

        


def exp_coefficient(N):
    '''exp()函数的系数  1/k!'''
    coefficient = [1]
    for k in range(1,N+1):
        coefficient.append( coefficient[-1]/k  )
    # 和下面的代码结果相同，但效率更高
    # import math
    # coefficient = [0]
    # for k in range(N+1):
    #     coefficient.append( 1/math.factorial(k)  )      
    return coefficient

def sin_coefficient(N):
    '''sin()函数的系数  '''
    coefficient_exp = exp_coefficient(N)
    coefficient_sin = []
    for k in range(0,N+1): #利用欧拉公式推出
        coefficient_sin.append( (complex(0,1)**k-(-complex(0,1))**k)/ (2*complex(0,1)) * coefficient_exp[k] ) 
    return coefficient_sin

def cos_coefficient(N):
    '''cos()函数的系数  '''
    coefficient_exp = exp_coefficient(N)
    coefficient_cos = []
    for k in range(0,N+1): #利用欧拉公式推出
        coefficient_cos.append( (complex(0,1)**k+(-complex(0,1))**k)/ 2 * coefficient_exp[k] ) 
    return coefficient_cos

def P106_3_2_coefficient(N):
    '''课本106页第2题 '''
    coefficient = []
    for k in range(0,N+1):
        coefficient.append( k / 6**k  )
    return coefficient

def Neumann_coefficient(N):
    ''' Neumann级数-系数  全是1 '''
    coefficient = []
    for k in range(0,N+1):
        coefficient.append( 1 )
    return coefficient

# ================================================================================
def matrix_function(A, coefficient):
    '''
    矩阵函数，基于若尔当标准型理论求
    '''
    
    A = Matrix(A)
    P, J = A.jordan_form() #A = PJ(P^-1)
    invP = P.inv()
       
    LEN = len(coefficient)
    Jk_list = [np.eye(A.shape[0])]
    for k in range(LEN - 1):
        Jk_list.append(np.dot(Jk_list[-1], J))
    
    fJ = 0
    for k in range(LEN):
        fJ = fJ + coefficient[k] * Jk_list[k] #f(J)
    
    fA = np.dot(np.dot(P, fJ), invP) #f(A) = P f(J) (P^-1)
    return fA
    
  
# ================================================================================

if __name__ == '__main__':
    #测试一下
    
    # 课本100页例3.1 改成求Neumann级数
    
    coefficient_Neumann = Neumann_coefficient(200)
    A = np.array([[0.1, 0.3], [0.7,0.6]])
    print('\n矩阵A的谱半径=', np.max(np.abs(np.linalg.eigvals(A))))
    print('课本100页例3.1 改成求Neumann级数f(A)=1/(I-A) =\n', matrix_function(A, coefficient_Neumann))
    print('验证直接求(I-A)^-1=\n', np.linalg.inv(np.eye(2)-A))
    print('\n')
    
    # ===============================================================
    
    
    # 课本106页第2题
    
    coefficient_P106_3_2 = P106_3_2_coefficient(200)
    A = np.array([[1, -8], [-2,1]])
    print('课本106页第2题f(A) =\n', matrix_function(A, coefficient_P106_3_2))
    print('\n')
    
    # ===============================================================
    
    # 课本107页例题，e^A,e^B
    
    coefficient_exp = exp_coefficient(200)
    A = np.array([[1, 1], [0,0]])
    B = np.array([[1, -1], [0,0]])
    print('课本107页例题，\ne^A =\n', matrix_function(A, coefficient_exp))
    print('e^B =\n', matrix_function(B, coefficient_exp))
    print('\n')
    
    # ===============================================================
  
    # 课本109页例题，例3.5
    
    t = 2.5
    A = np.array([[2,0,0],[1,1,1],[1,-1,3]])
    tA = t * A
    e_tA_1 = matrix_function(tA, coefficient_exp)
    print('课本109页例题，例3.5，t = ',t,', e^tA =\n', e_tA_1)
    e_tA_2 = np.exp(2 * t) * np.array([[1,0,0],[t,1-t,t],[t,-t,1+t]]) 
    print('验证直接求e^tA=\n', e_tA_2)
    print('求范数验证||e^tA_1 - e^tA_2||=', np.linalg.norm(e_tA_1 - e_tA_2, 1))
    print('\n')
    
    # ===============================================================
    
    
    # 课本110页例题，例3.6
    coefficient_sin = sin_coefficient(200)
    A = np.zeros((4,4))
    A[0,0]=np.pi; A[1,1] = -np.pi; A[2,3]=1
    sinA_1 = matrix_function(A, coefficient_sin)
    print('课本110页例题，例3.6，sinA =\n', sinA_1)
    sinA_2 = np.zeros((4,4))
    sinA_2[2,3] = 1
    print('验证直接求sinA=\n', sinA_2)
    print('求范数验证||sinA_1 - sinA_2||=', np.linalg.norm(sinA_1 - sinA_2, 1))
    print('\n')
    
    
    # ===============================================================
    from numpy import cos as cos
    
    print(cos(1))
    # 课本111页例题，例3.7
    coefficient_cos = cos_coefficient(200)
    A = np.array([[4,6,0],[-3,-5,0],[-3,-6,1]])
    cosA_1 = matrix_function(A, coefficient_cos)
    print('课本111页例题，例3.7，cosA =\n', cosA_1)
    cosA_2 = np.array([[2*cos(1)-cos(2),2*cos(1)-2*cos(2),0],
                       [cos(2)-cos(1),  2*cos(2)-cos(1),  0],
                       [cos(2)-cos(1),  2*cos(2)-2*cos(1),cos(1)]])
    print('验证直接求cosA=\n', cosA_2)
    print('求范数验证||cosA_1 - cosA_2||=', np.linalg.norm(cosA_1 - cosA_2, 1))

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    