# -*- coding: utf-8 -*-


import numpy as np
import torch
import torch.nn as nn
# import torch.nn.functional as F
# import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
# from torch.autograd import Variable
# from torchvision import transforms
from google.colab import drive         
from PIL import Image
import matplotlib . pyplot as plt
# http://pytorch.org/
from os.path import exists
from wheel.pep425tags import get_abbr_impl, get_impl_ver, get_abi_tag
platform = '{}{}-{}'.format(get_abbr_impl(), get_impl_ver(), get_abi_tag())
cuda_output = !ldconfig -p|grep cudart.so|sed -e 's/.*\.\([0-9]*\)\.\([0-9]*\)$/cu\1\2/'
accelerator = cuda_output[0] if exists('/dev/nvidia0') else 'cpu'
!pip3 install https://download.pytorch.org/whl/cu100/torch-1.0.1-cp36-cp36m-linux_x86_64.whl
!pip3 install torchvision
  
device =  torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)

# Use this if you are working on COLAB
# This will prompt for authorization.
drive.mount('/content/drive')

# %cd "/content/drive/My Drive/data"
!ls

def extract_data(x_data_filepath, y_data_filepath):
    X = np.load(x_data_filepath)
    y = np.load(y_data_filepath)
    return X, y
  
def data_visualization(images,labels):
  """
    Visualize 6 pictures per class using your prefered visulization library (matplotlib, etc)

    Args:
        images: training images in shape (num_images,3,image_H,image_W)
        labels: training labels in shape (num_images,)
    """
  
  
  plt.figure()
  fig, ax = plt.subplots(5,6,figsize=(20,20))
  l = list(labels)

  
  imgs = {0.0:0,1.0:0,2.0:0,3.0:0,4.0:0}
  p = 0
  for i,lab in enumerate(l):
        
        if sum(imgs.values()) == 30:
          break

        if imgs[l[i]] >= 6:
          continue
        imgs[l[i]] = imgs[l[i]] + 1


        im = np.transpose(images[i,:], (1,2,0))
        p = int(6*l[i]+imgs[l[i]])
#         print(p)
#         print(np.shape(im))
        plt.subplot(5,6,p)
        plt.xlabel('Label {}'.format(int(l[i])+1))
        plt.imshow(im)



#          plt.xlabel(img, fontsize=9)
  print(imgs)
  plt.show()
    


#

###########################################################
# Extracting and loading data
############################################################
class Dataset(Dataset):
    def __init__(self, X, y):
        self.len = len(X)           
        if torch.cuda.is_available():
          self.x_data = torch.from_numpy(X).float().cuda()
          self.y_data = torch.from_numpy(y).long().cuda()
        else:
          self.x_data = torch.from_numpy(X).float()
          self.y_data = torch.from_numpy(y).long()
    
    def __len__(self):
        return self.len

    def __getitem__(self, idx):
        return self.x_data[idx], self.y_data[idx]

def create_validation(x_train,y_train):
  """
    Randomly choose 20 percent of the training data as validation data.

    Args:
        x_train: training images in shape (num_images,3,image_H,image_W)
        y_train: training labels in shape (num_images,)
    Returns:
        new_x_train: training images in shape (0.8*num_images,3,image_H,image_W)
        new_y_train: training labels in shape (0.8*num_images,)
        x_val: validation images in shape (0.2*num_images,3,image_H,image_W)
        y_val: validation labels in shape (0.2*num_images,)
    """
  dataset_size = len(y_train)
  indices = list(range(dataset_size))
  validation_split = 0.2
  split = int(np.floor(validation_split * dataset_size))
  np.random.seed(5)
  np.random.shuffle(indices)
  train_indices, val_indices = indices[split:], indices[:split]
  
  print(len(train_indices))
  print(len(val_indices))


  new_x_train = x_train[train_indices,:]
  new_y_train = y_train[train_indices]
  
  x_val = x_train[val_indices,:]
  y_val = y_train[val_indices]
  
  return new_x_train,new_y_train,x_val,y_val

############################################################
# Feed Forward Neural Network
############################################################
class FeedForwardNN(nn.Module):
    """ 
        (1) Use self.fc1 as the variable name for your first fully connected layer
        (2) Use self.fc2 as the variable name for your second fully connected layer
    """
    def __init__(self,input_size = 16320 , hidden_size=2000, num_classes =5):
      super(FeedForwardNN, self).__init__()

      self.fc1 = nn.Linear(input_size, hidden_size)
      self.relu = nn.ReLU()
      self.fc2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
      
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)

        return out

    """ 
        Please do not change the functions below. 
        They will be used to test the correctness of your implementation 
    """
    def get_fc1_params(self):
        return self.fc1.__repr__()
    
    def get_fc2_params(self):
        return self.fc2.__repr__()

############################################################
# Convolutional Neural Network
############################################################
class ConvolutionalNN(nn.Module):
    """ 
        (1) Use self.conv1 as the variable name for your first convolutional layer
        (2) Use self.pool1 as the variable name for your first pooling layer
        (3) Use self.conv2 as the variable name for your second convolutional layer
        (4) Use self.pool2 as the variable name for you second pooling layer  
        (5) Use self.fc1 as the variable name for your first fully connected laye
        (6) Use self.fc2 as the variable name for your second fully connected layer
    """
    def __init__(self):
        super(ConvolutionalNN, self).__init__()
        self.conv1 = nn.Conv2d(in_channels = 3, out_channels=16, kernel_size=3,stride=1, padding=0)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(kernel_size=2)
        self.drop_out1 = nn.Dropout(0.4)

        self.conv2 = nn.Conv2d(in_channels = 16, out_channels= 32,kernel_size= 3,stride=1, padding=0)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(kernel_size=2)
        self.drop_out2 = nn.Dropout(0.4)

        
        self.fc1 = nn.Linear(8512, 200)
        self.relu3 = nn.ReLU()
        self.fc2 = nn.Linear(200, 5)

    def forward(self, x):
      
        out = self.conv1(x)
        out = self.relu1(out)
        out = self.pool1(out)
        out = self.drop_out1(out)

        out = self.conv2(out)
        out = self.relu2(out)
        out = self.pool2(out)
        out = self.drop_out2(out)
        
        out = out.reshape(out.size(0), -1)
        out = self.fc1(out)
        out = self.relu3(out)
        out = self.fc2(out)    
        
        return out
      
    """ 
        Please do not change the functions below. 
        They will be used to test the correctness of your implementation
    """
    
    def get_conv1_params(self):
        return self.conv1.__repr__()
    
    def get_pool1_params(self):
        return self.pool1.__repr__()

    def get_conv2_params(self):
        return self.conv2.__repr__()
      
    def get_pool2_params(self):
        return self.pool2.__repr__()
      
    def get_fc1_params(self):
        return self.fc1.__repr__()
    
    def get_fc2_params(self):
        return self.fc2.__repr__()

def normalize_image(image):
  """
    Normalize each input image

    Args:
        image: the input image in shape (3,image_H,image_W)
    Returns:
        norimg: the normalized image in the same shape as the input
        
    """
#   print(np.shape(image[0]))
  
#   img_mean = torch.mean(image[0],axis=(1,2))
  
#   image_mean = image[0].mean((1,2)) #Shape (N,3)
  image_mean0 = image[0,0].mean() #Shape (N,3)
  image_mean1 = image[0,1].mean() #Shape (N,3)
  image_mean2 = image[0,2].mean() #Shape (N,3)
  
  
  
  
  image_std0 = image[0,0].std() #Shape (N,3)
  image_std1 = image[0,1].std() #Shape (N,3)
  image_std2 = image[0,2].std() #Shape (N,3)

#   print(image_std0)
#   print(image_std1)

#   channel_mean =image_mean
#   print('Mean {}'.format(channel_mean[0]))
    
  image[0,0,:] = (image[0,0,:] - image_mean0 )/image_std0
  image[0,1,:] = (image[0,1,:] - image_mean1 )/image_std1
  image[0,2,:] = (image[0,2,:] - image_mean2 )/image_std2
  norimg = image
#   print(np.shape(norimg))


  
#   image_mean = image.mean((1,2)) #Shape (N,3)
#   image_std0 = image[0].std() #Shape (N,3)
#   image_std1 = image[1].std() #Shape (N,3)
#   image_std2 = image[2].std() #Shape (N,3)

# #   print(image_std0)
# #   print(image_std1)

#   channel_mean =image_mean
# #   print('Mean {}'.format(channel_mean[0]))
    
#   image[0,:] = (image[0,:] - channel_mean[0] )/image_std0
#   image[1,:] = (image[1,:] - channel_mean[1] )/image_std1
#   image[2,:] = (image[2,:] - channel_mean[2] )/image_std2
#   norimg = image



  return norimg

############################################################
# Optimized Neural Network
############################################################
class OptimizedNN(nn.Module):
    def __init__(self):
        super(OptimizedNN, self).__init__()
        self.conv1 = nn.Conv2d(in_channels = 3, out_channels=16, kernel_size=3,stride=1, padding=0)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(kernel_size=2)

        self.conv2 = nn.Conv2d(in_channels = 16, out_channels= 32,kernel_size= 3,stride=1, padding=0)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(kernel_size=2)
        
        self.fc1 = nn.Linear(8512, 200)
        self.relu3 = nn.ReLU()
        self.fc2 = nn.Linear(200, 5)

    def forward(self, x):
      
        out = self.conv1(x)
        out = self.relu1(out)
        out = self.pool1(out)
        out = self.conv2(out)
        out = self.relu2(out)
        out = self.pool2(out)
        out = out.view(-1, 8512)
        out = self.fc1(out)
        out = self.relu3(out)
        out = self.fc2(out)    
        
        return out
      
    """ 
        Please do not change the functions below. 
        They will be used to test the correctness of your implementation
    """
    
    def get_conv1_params(self):
        return self.conv1.__repr__()
    
    def get_pool1_params(self):
        return self.pool1.__repr__()

    def get_conv2_params(self):
        return self.conv2.__repr__()
      
    def get_pool2_params(self):
        return self.pool2.__repr__()
      
    def get_fc1_params(self):
        return self.fc1.__repr__()
    
    def get_fc2_params(self):
        return self.fc2.__repr__()

def train_val_NN(model, train_loader, validation_loader, loss_function, optimizer,num_epochs):
  """
    Runs experiment on the model neural network given a train loader, loss function and optimizer and find validation accuracy for each epoch given the validation_loader.

    Args:
        neural_network (NN model that extends torch.nn.Module): For example, it should take an instance of either
                                                                FeedForwardNN or ConvolutionalNN,
        train_loader (DataLoader),
        validation_loader (DataLoader),
        loss_function (torch.nn.CrossEntropyLoss),
        optimizer (optim.SGD)
        num_epochs (number of iterations)
    Returns:
        tuple: First position, training accuracies of each epoch formatted in an array of shape (num_epochs,1).
               Second position, training loss of each epoch formatted in an array of shape (num_epochs,1).
               third position, validation accuracy of each epoch formatted in an array of shape (num_epochs,1).
               
    """
  Loss=[]
  TA = []
  VA = []
  for epoch in range(num_epochs):
        for i, (images, labels) in enumerate(train_loader):
        
            images = images.to(device)
#             images = images.reshape(-1, 16320).to(device)

            images = normalize_image(images)

            labels = labels.to(device)
            
            
            # Load images
#             images = images.requires_grad_()
            model.train()


            # Forward pass to get output/logits
            outputs = model(images)

            # Calculate Loss: softmax --> cross entropy loss
            loss = loss_function(outputs, labels)
       
            # Clear gradients w.r.t. parameters
            optimizer.zero_grad()


            # Getting gradients w.r.t. parameters
            loss.backward()

            # Updating parameters
            optimizer.step()

       
        correct = 0
        total = 0
            # Iterate through test dataset
        for images, labels in validation_loader:
            images = images.to(device)
#             images = images.reshape(-1, 16320).to(device)

            images = normalize_image(images)

            labels = labels.to(device)
            # Load images
#             images = images.requires_grad_()

            # Forward pass only to get logits/output
            model.eval()
            outputs = model(images)

            # Get predictions from the maximum value
            _, predicted = torch.max(outputs.data, 1)

            # Total number of labels
            total += labels.size(0)

            # Total correct predictions
            correct += (predicted == labels).sum()

        val_accuracy = 100 * correct / total
        loss_np = loss.item()
        Loss.append(loss_np)
        VA.append(val_accuracy)
        
        
               
        correct = 0
        total = 0
        
        for images, labels in train_loader:
            images = images.to(device)
#             images = images.reshape(-1, 16320).to(device)
           
            images = normalize_image(images)

            labels = labels.to(device)
            # Load images
#             images = images.requires_grad_()
            model.eval()
            # Forward pass only to get logits/output
            outputs = model(images)

            # Get predictions from the maximum value
            _, predicted = torch.max(outputs.data, 1)

            # Total number of labels
            total += labels.size(0)

            # Total correct predictions
            correct += (predicted == labels).sum()

        train_accuracy = 100 * correct / total
        TA.append(train_accuracy)

                # Print Loss
        print('Epoch: {}. Loss: {}. Train_Accuracy: {}.Val_Accuracy: {}.'.format(epoch, loss_np,train_accuracy, val_accuracy))
        info = { 'loss': loss_np, 'tr_accuracy': train_accuracy ,'val_accuracy': val_accuracy}

        for tag, value in info.items():
            logger.scalar_summary(tag, value, epoch+1)
        
  np.savetxt('TA.txt', TA, fmt='%f')
  np.savetxt('Loss.txt', Loss, fmt='%f')
  np.savetxt('VA.txt', VA, fmt='%f')


  return TA,Loss,VA

def test_NN(model, test_loader, loss_function):
  
  """
    Runs experiment on the model neural network given a test loader, loss function and optimizer.

    Args:
        neural_network (NN model that extends torch.nn.Module): For example, it should take an instance of either
                                                                FeedForwardNN or ConvolutionalNN,
        test_loader (DataLoader), (make sure the loader is not shuffled)
        loss_function (torch.nn.CrossEntropyLoss),
        optimizer (your choice)
        num_epochs (number of iterations)
    Returns:
        your predictions         
    """
  
  with torch.no_grad():
    preds = []
    total = 0
    for images,labels in test_loader:
        images = images.to(device)
        images = normalize_image(images)
        model.eval()
        outputs = model(images)
        _, predicted = torch.max(outputs.data, 1)
        preds.append(predicted)

#     print('Accuracy of the network on the 10000 test images: {} %'.format(100 * correct / total))

  return preds

import tensorflow as tf
import numpy as np
import scipy.misc 
import requests


try:
    from StringIO import StringIO  # Python 2.7
except ImportError:
    from io import BytesIO         # Python 3.x


class Logger(object):
    
    def __init__(self, log_dir):
        """Create a summary writer logging to log_dir."""
        self.writer = tf.summary.FileWriter(log_dir)

    def scalar_summary(self, tag, value, step):
        """Log a scalar variable."""
        summary = tf.Summary(value=[tf.Summary.Value(tag=tag, simple_value=value)])
        self.writer.add_summary(summary, step)

    def image_summary(self, tag, images, step):
        """Log a list of images."""

        img_summaries = []
        for i, img in enumerate(images):
            # Write the image to a string
            try:
                s = StringIO()
            except:
                s = BytesIO()
            scipy.misc.toimage(img).save(s, format="png")

            # Create an Image object
            img_sum = tf.Summary.Image(encoded_image_string=s.getvalue(),
                                       height=img.shape[0],
                                       width=img.shape[1])
            # Create a Summary value
            img_summaries.append(tf.Summary.Value(tag='%s/%d' % (tag, i), image=img_sum))

        # Create and write Summary
        summary = tf.Summary(value=img_summaries)
        self.writer.add_summary(summary, step)
        
    def histo_summary(self, tag, values, step, bins=1000):
        """Log a histogram of the tensor of values."""

        # Create a histogram using numpy
        counts, bin_edges = np.histogram(values, bins=bins)

        # Fill the fields of the histogram proto
        hist = tf.HistogramProto()
        hist.min = float(np.min(values))
        hist.max = float(np.max(values))
        hist.num = int(np.prod(values.shape))
        hist.sum = float(np.sum(values))
        hist.sum_squares = float(np.sum(values**2))

        # Drop the start of the first bin
        bin_edges = bin_edges[1:]

        # Add bin edges and counts
        for edge in bin_edges:
            hist.bucket_limit.append(edge)
        for c in counts:
            hist.bucket.append(c)

        # Create and write Summary
        summary = tf.Summary(value=[tf.Summary.Value(tag=tag, histo=hist)])
        self.writer.add_summary(summary, step)
        self.writer.flush()

! rm -r ./logs
LOG_DIR = './logs'
get_ipython().system_raw(
    'tensorboard --logdir {} --host 0.0.0.0 --port 6006 &'
    .format(LOG_DIR)
)

!if [ -f ngrok ] ; then echo "Ngrok already installed" ; else wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip > /dev/null 2>&1 && unzip ngrok-stable-linux-amd64.zip > /dev/null 2>&1 ; fi

get_ipython().system_raw('./ngrok http 6006 &')

! curl -s http://localhost:4040/api/tunnels | python3 -c \
    "import sys, json; print('Tensorboard Link: ' +str(json.load(sys.stdin)['tunnels'][0]['public_url']))"
    
    
logger = Logger('./logs')
logger2 = Logger('./logs1')

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)

model = ConvolutionalNN().to(device)
loss_function = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)  
# optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

num_epochs = 40

x_data_filepath = 'images_train.npy'
y_data_filepath = 'labels_train.npy'
X,y = extract_data(x_data_filepath, y_data_filepath)

new_x_train,new_y_train,x_val,y_val = create_validation(X,y)

trainset = Dataset(new_x_train, new_y_train)
valset = Dataset(x_val, y_val)

train_loader = DataLoader(dataset=trainset,batch_size=1, shuffle=True)
validation_loader = DataLoader(dataset=valset,batch_size=1, shuffle=True)

[TA,Loss,VA] =train_val_NN(model, train_loader, validation_loader, loss_function, optimizer,num_epochs)

plt.figure()
plt.plot(Loss,label="train loss")
plt.legend(loc='best')

plt.show()
plt.figure()

plt.plot(TA,label="train accuracy")
plt.plot(VA,label="validation accuracy")

plt.legend(loc='best')

plt.show()


xtest_data_filepath = 'images_test.npy'
Xtest = np.load(xtest_data_filepath)
ytest = new_y_train[0:np.shape(Xtest)[0]]
print(np.shape(y_val))

testset = Dataset(Xtest,ytest)
test_loader = DataLoader(dataset=testset,batch_size=1, shuffle=False)

pred = test_NN(model, test_loader, loss_function)
print(pred)

np.savetxt('HW4_preds.txt', pred, fmt='%d')

plt.figure()

plt.plot(TA,label="train accuracy")
plt.plot(VA,label="validation accuracy")

plt.legend(loc='best')

plt.show()

# Run Baseline CNN

# Run Baseline CNN on Normilized Images

# Choose from one of the above models and improve its performance
