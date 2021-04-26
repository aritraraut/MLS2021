# -*- coding: utf-8 -*-
"""DLClassTest.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19xdPkyEz0zwCdGsXcxPuc9FmuIBPdCLl
"""

import torch
from torch import nn,optim
from matplotlib.pyplot

!git clone https://github.com/YoongiKim/CIFAR-10-images

#check if cuda is available
train_on_gpu=torch.cuda.is_available()

if not train_on_gpu:
  print("CUDA is not available,training on cpu")
else :
  print('CUDA is available,training on gpu')

## Making the CSV files

import os
p=[]
c=[]

for file_name in os.listdir("CIFAR-10-images/test/"):
  for files in os.listdir("CIFAR-10-images/test/"+file_name):
    if files.split(".")[-1].lower() in {"jpeg", "jpg", "png"}:
        path='CIFAR-10-images/test/'+file_name+'/'+files
        clss=file_name
        p.append(path)
        c.append(clss)

p1=[]
c1=[]

for file_name in os.listdir("CIFAR-10-images/train/"):
  for files in os.listdir("CIFAR-10-images/train/"+file_name):
    if files.split(".")[-1].lower() in {"jpeg", "jpg", "png"}:
        path='CIFAR-10-images/train/'+file_name+'/'+files
        clss=file_name
        p1.append(path)
        c1.append(clss)


import pandas as pd
test_dataset=pd.DataFrame({'path':p,'class':c})
train_dataset=pd.DataFrame({'path':p1,'class':c1})

test_d = test_dataset.to_csv('test_data.csv', index=False)
train_d = train_dataset.to_csv('train_data.csv', index=False)

## Custom dataloader

import numpy as np
import imageio
import csv

class MyDataset():
  def __init__(self,image_set,argument=True):
    with open(image_set,"r") as csv_handle:
      csv_reader = csv.reader(csv_handle,delimiter=",")
      self.imgfiles=[eachline[0] for eachline in csv_reader]
    self.argument=argument
  def __len__(self):
    return len(self.imgfiles)
  def __gititem__(self,idx):
    img=imageio.imread(self.imgfiles[idx])
    X=np.asarray(img,dtype=np.float32)
    if self.argument:
      X=do_yarn_transform(X)
    Y=self.classlabels[idx]
    return X,Y

train_data=MyDataset('train_data.csv')
test_data=MyDataset('test_data.csv')

train_data[0]

import torchvision.transforms as transforms
from torch.utils.data.sampler import SubsetRandomSampler

# obtain training indices that will be used for validation
num_train = len(train_data)
indices = list(range(num_train))
np.random.shuffle(indices)
split = int(np.floor(valid_size * num_train))
train_idx, valid_idx = indices[split:], indices[:split]

# define samplers for obtaining training and validation batches
train_sampler = SubsetRandomSampler(train_idx)
valid_sampler = SubsetRandomSampler(valid_idx)

batch_size=20
num_workers=0
valid_size=0.2

train_loader = torch.utils.data.DataLoader(train_data, batch_size=batch_size,
    sampler=train_sampler, num_workers=num_workers)
valid_loader = torch.utils.data.DataLoader(train_data, batch_size=batch_size, 
    sampler=valid_sampler, num_workers=num_workers)
test_loader = torch.utils.data.DataLoader(test_data, batch_size=batch_size, 
    num_workers=num_workers)

train_loader

import torch.nn.functional as F

class CNN(nn.Module):
  def __init__(self):
    super(CNN,self).__init__()
    self.conv1=nn.Conv2d(3,16,3,padding=1)
    self.conv2=nn.Conv2d(16,32,3,padding=1)
    self.conv3=nn.Conv2d(32,64,3,padding=1)
    self.pool=nn.MaxPool2d(2,2)
    self.fc1=nn.Linear(64*4*4,500)
    self.fc2=nn.Linear(500,10)
    self.dropout=nn.Dropout(0.25)
  def forward(self,x):
    x=self.pool(F.relu(self.conv1(x)))
    x=self.pool(F.relu(self.conv2(x))) 
    x=self.pool(F.relu(self.conv3(x)))
    x=x.view(-1,64*4*4)  #flattening
    x=self.dropout(x) 
    x=F.relu(self.fc1(x))
    x=self.dropout(x)
    x=F.relu(self.fc2(x))
    
    return x

# create a complete CNN
model = CNN()
print(model)

# move tensors to GPU if CUDA is available
if train_on_gpu:
    model.cuda()

# specify loss function (categorical cross-entropy)
criterion = nn.CrossEntropyLoss()

# specify optimizer
optimizer = optim.SGD(model.parameters(), lr=0.01)

# number of epochs to train the model
n_epochs = 30

valid_loss_min = np.Inf # track change in validation loss

for epoch in range(1, n_epochs+1):

    # keep track of training and validation loss
    train_loss = 0.0
    valid_loss = 0.0
    
    ###################
    # train the model #
    ###################
    model.train()
    for data, target in train_loader:
        # move tensors to GPU if CUDA is available
        if train_on_gpu:
            data, target = data.cuda(), target.cuda()
        # clear the gradients of all optimized variables
        optimizer.zero_grad()
        # forward pass: compute predicted outputs by passing inputs to the model
        output = model(data)
        # calculate the batch loss
        loss = criterion(output, target)
        # backward pass: compute gradient of the loss with respect to model parameters
        loss.backward()
        # perform a single optimization step (parameter update)
        optimizer.step()
        # update training loss
        train_loss += loss.item()*data.size(0)
        
    ######################    
    # validate the model #
    ######################
    model.eval()
    for data, target in valid_loader:
        # move tensors to GPU if CUDA is available
        if train_on_gpu:
            data, target = data.cuda(), target.cuda()
        # forward pass: compute predicted outputs by passing inputs to the model
        output = model(data)
        # calculate the batch loss
        loss = criterion(output, target)
        # update average validation loss 
        valid_loss += loss.item()*data.size(0)
    
    # calculate average losses
    train_loss = train_loss/len(train_loader.sampler)
    valid_loss = valid_loss/len(valid_loader.sampler)
        
    # print training/validation statistics 
    print('Epoch: {} \tTraining Loss: {:.6f} \tValidation Loss: {:.6f}'.format(
        epoch, train_loss, valid_loss))
    
    # save model if validation loss has decreased
    if valid_loss <= valid_loss_min:
        print('Validation loss decreased ({:.6f} --> {:.6f}).  Saving model ...'.format(
        valid_loss_min,
        valid_loss))
        torch.save(model.state_dict(), 'model_cifar.pt')
        valid_loss_min = valid_loss

