# -*- coding: utf-8 -*-
'''
矩阵克罗内克积
'''


import numpy as np
 
# 定义两个矩阵
A = np.array([[1, 2]])
B = np.array([[1, 2], [3, 4]])
 
# 计算克洛内克积  (aij * B)
C = np.kron(A, B)
 
print(C)



