# -*- coding: utf-8 -*-
"""Denoiser.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FpnseDngvPkDY9F1KAu5xwAcb-_8u8m6
"""

import numpy 
import math
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense
from keras.datasets import mnist
import cv2
(X_train, y_train), (X_test, y_test) = mnist.load_data()
num_pixels = X_train.shape[1] * X_train.shape[2]
X_train = X_train.reshape(X_train.shape[0], num_pixels).astype('float32')
X_test = X_test.reshape(X_test.shape[0], num_pixels).astype('float32')
X_train = X_train / 255
X_test = X_test / 255
dneural = numpy.zeros(5)
noise_factor = 1
stdv = 0
for i in range(5):
  stdv = stdv+20/255
  x_train_noisy = X_train + noise_factor * numpy.random.normal(loc=0.0, scale=stdv, size=X_train.shape)
  x_test_noisy = X_test + noise_factor * numpy.random.normal(loc=0.0, scale=stdv, size=X_test.shape)
  x_train_noisy = numpy.clip(x_train_noisy, 0., 1.)
  x_test_noisy = numpy.clip(x_test_noisy, 0., 1.)
  # create model
  model = Sequential()
  model.add(Dense(500, input_dim=num_pixels, activation='relu'))
  model.add(Dense(300, activation='relu'))
  model.add(Dense(100, activation='relu'))
  model.add(Dense(300, activation='relu'))
  model.add(Dense(500, activation='relu'))
  model.add(Dense(784, activation='sigmoid'))
  # Compile the model
  model.compile(loss='mean_squared_error', optimizer='adam', metrics='accuracy')
  model.fit(x_train_noisy, X_train, validation_data=(x_test_noisy, X_test), epochs=20, batch_size=100)
  pred = model.predict(x_test_noisy)
  # X_test = numpy.reshape(X_test, (10000,28,28)) *255
  # pred = numpy.reshape(pred, (10000,28,28)) *255
  # x_test_noisy = numpy.reshape(x_test_noisy, (-1,28,28)) *255
  # plt.figure(figsize=(20, 4))
  def psnr(img1, img2):
      mse = numpy.mean((img1 - img2) ** 2)
      if mse == 0:
          return 100
      PIXEL_MAX = 255.0
      return 20 * math.log10(PIXEL_MAX / math.sqrt(mse))
  temp = 0
  for k in range(10,20,1):
    temp = temp + psnr(X_test[k,:]*255,pred[k,:]*255)
  dneural[i] = temp/10
# print("Test Images")
# for i in range(10,20,1):
#     plt.subplot(2, 10, i+1)
#     plt.imshow(X_test[i,:,:], cmap='gray')
#     curr_lbl = y_test[i]
#     plt.title("(Label: " + str(curr_lbl) + ")")
# plt.show()    
# plt.figure(figsize=(20, 4))
# print("Test Images with Noise")
# for i in range(10,20,1):
#     plt.subplot(2, 10, i+1)
#     plt.imshow(x_test_noisy[i,:,:], cmap='gray')
# plt.show()    
# plt.figure(figsize=(20, 4))
# print("Reconstruction of Noisy Test Images")
# for i in range(10,20,1):
#     plt.subplot(2, 10, i+1)
#     plt.imshow(pred[i,:,:], cmap='gray')  
# plt.show()

from scipy import ndimage
from skimage.restoration import denoise_nl_means, estimate_sigma, denoise_tv_bregman
dgauss = numpy.zeros(5)
dmedian = numpy.zeros(5)
dnlm = numpy.zeros(5)
dtv = numpy.zeros(5)
stdv = 0
for i in range(5):
  stdv = stdv + 20/255
  x_test_noisy = X_test + noise_factor * numpy.random.normal(loc=0.0, scale=stdv, size=X_test.shape)
  x_test_noisy = numpy.clip(x_test_noisy, 0., 1.)
  sigma_est = numpy.mean(estimate_sigma(x_test_noisy))
  pred = ndimage.gaussian_filter(x_test_noisy, sigma=sigma_est)
  pred2 = ndimage.median_filter(x_test_noisy, size=2)
  pred3 = denoise_nl_means(x_test_noisy, patch_distance=5,sigma=sigma_est,fast_mode=True)
  pred4 = denoise_tv_bregman(x_test_noisy,weight=5)
  temp = 0
  temp2 = 0
  temp3 = 0
  temp4 = 0
  for k in range(10,20,1):
    temp = temp + psnr(X_test[k,:]*255,pred[k,:]*255)
    temp2 = temp2 + psnr(X_test[k,:]*255,pred2[k,:]*255)
    temp3 = temp3 + psnr(X_test[k,:]*255,pred3[k,:]*255)
    temp4 = temp4 + psnr(X_test[k,:]*255,pred4[k,:]*255)
  dgauss[i] = temp/10
  dmedian[i] = temp2/10
  dnlm[i] = temp3/10
  dtv[i] = temp4/10
plt.figure()
x = numpy.array([20,40,60,80,100])
plt.plot(x,dgauss,'r-',linewidth=2)
plt.plot(x,dmedian,'b-',linewidth=2)
plt.plot(x,dneural,'g-',linewidth=2)
plt.plot(x,dnlm,'k-',linewidth=2)
plt.plot(x,dtv,'y-',linewidth=2)
plt.legend(['Gaussian Filter','Median Filter','Deep Neural Network','NLM','TV'])
plt.xlabel('$\sigma$')
plt.ylabel('PSNR (dB)')
plt.grid()

# PnP ADMM
print("Test Images")
i = 10  #Image number
X_test = numpy.reshape(X_test, (10000,28,28)) *255
pred = numpy.reshape(pred, (10000,28,28)) *255
pred2 = numpy.reshape(pred2, (10000,28,28)) *255
x_test_noisy = numpy.reshape(x_test_noisy, (-1,28,28)) *255
plt.subplot(2, 10, 1)
plt.imshow(X_test[i,:,:], cmap='gray')
curr_lbl = y_test[i]
plt.title("(Label: " + str(curr_lbl) + ")")
plt.show()    
print("Noisy Image")
plt.subplot(2, 10, 2)
plt.imshow(x_test_noisy[i,:,:], cmap='gray')
plt.show()    
print("Gaussian Filter")
plt.subplot(2, 10, 3)
plt.imshow(pred[i,:,:], cmap='gray')  
plt.show()
plt.figure(figsize=(20, 4))
print("Median Filter")
plt.subplot(2, 10, 3)
plt.imshow(pred2[i,:,:], cmap='gray')  
plt.show()