# -*- coding: utf-8 -*-
import numpy as np
x_data = np.float32(np.random.rand(100,2)) #使用NumPy生成数据
y_data = (np.dot(x_data,[0.100, 0.200]) + 0.300).reshape(-1,1) #y=w1*x1+w2*x2+b

'''利用sklearn算法包实现多元线性回归, 并求系数'''
import sklearn.linear_model as skl
model = skl.LinearRegression() #调用线性回归模型
model.fit(x_data, y_data) #模型训练
y_predict = model.predict(x_data)#预测

print('求范数检验模型预测结果||y_predict - y_data||=', np.linalg.norm(y_predict - y_data))
print('训练得到的线性模型 y = w1*x1 + w2*x2 + b，其系数为')
print('w1=',model.coef_[0][0],',w2=',model.coef_[0][1],',b=',model.intercept_[0])

''''' 最小二乘拟合：通过对损失函数求导计算系数 W = (X^(T)*X)^(-1) * X * Y''''' 
X = np.hstack((x_data, np.ones([y_data.shape[0],1])))
W = np.dot(np.linalg.inv(np.dot(X.transpose(), X)),np.dot(X.transpose(), y_data))

print('\n最小二乘拟合：通过对损失函数求导计算系数 W ')
print('损失函数为loss(W) = (Y-XW)^(T) *(Y-XW),  是凸函数，求极小')
print('求出dloss/dW =  2X^(T)*(XW - Y)，令 dloss/dW = 0， 解得W = (X^(T)*X)^(-1) * X^(T) * Y')
print('w1=',W[0][0],',w2=',W[1][0],',b=',W[2][0])

''''' 方法三：利用广义逆求解 XW = Y，得 W =  X^(+) * Y (其中X^(+)为X的广义逆，第六章还会讲)''''' 
W = np.dot(np.linalg.pinv(X),y_data)#利用广义逆求系数
print('\n方法三：利用广义逆求解XW = Y，得 W =  X^(+) * Y (其中X^(+)为X的广义逆，第六章还会讲)')
print('w1=',W[0][0],',w2=',W[1][0],',b=',W[2][0])
  