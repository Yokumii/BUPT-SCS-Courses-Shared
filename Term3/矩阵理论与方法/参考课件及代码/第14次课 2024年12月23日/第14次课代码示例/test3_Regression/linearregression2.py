# -*- coding: utf-8 -*-
#!/usr/bin/python

from __future__ import division

import numpy as np  
from sklearn.model_selection import train_test_split

data   = []  
labels = []  

with open("data.txt") as ifile:  
        for line in ifile:  
            tokens = line.strip().split('\t')  
            if tokens!=['']:
                data.append([float(tk) for tk in tokens[:-1]])  
                labels.append(tokens[-1]) 
x = np.array(data) 
y = np.double(labels)

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.01) 


''''' LinearRegression '''  
'''利用矩阵广义逆实现多元线性回归'''
X=np.hstack((x_train,np.ones([y_train.shape[0],1])))
Y=y_train.reshape(-1,1)

W=np.dot(np.linalg.pinv(X),Y)#利用广义逆求系数

w=W[0:4]
b=W[4]

print('w=',w.transpose(),'b=',b)

y_predict_train=np.dot(x_train,w)+b
''''' LinearRegression '''  



N=y_train.size
X=range(0,N)
Y1=np.double(y_train)
Y2=np.double(y_predict_train)[:,0]

GError=np.abs(Y1-Y2)


RMSE=np.sqrt(np.dot(GError,GError)/N)

print("RMSE_train=", RMSE)



import matplotlib.pyplot as plt  



#y_predict=lr.predict(x_test)
y_predict=np.dot(x_test,w)+b

N=y_test.size
X=range(0,N)
Y1=np.double(y_test)
Y2=np.double(y_predict)[:,0]

GError=np.abs(Y1-Y2)
RMSE=np.sqrt(np.dot(GError,GError)/N)

print("RMSE_test=", RMSE)




fig1 = plt.figure('fig1')
plt.plot(X,GError)
#plt.scatter(X,Y1,marker='o',c='b')
#plt.scatter(X,Y2,marker='o',c='r')


fig2 = plt.figure('fig2')
plt.plot(X,Y1,'b',lw=1)
plt.plot(X,Y2,'r+')


