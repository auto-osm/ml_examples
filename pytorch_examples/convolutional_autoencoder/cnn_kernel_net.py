#!/usr/bin/env python

import sys
sys.path.append('../pytorch_load_image/')
import torch
from torch.autograd import Variable
import numpy as np
import torch.nn.functional as F
import matplotlib
from img_load import *


class cnn_kernel_net(torch.nn.Module):
	def __init__(self, db, learning_rate=0.001):
		super(cnn_kernel_net, self).__init__()
		self.db = db
		filter_len = 5
		self.training_mode = 'autoencoder'		#	autoencoder vs kernel_net
		[H,W] = self.extract_HW(db)

		self.conv1 = nn.Conv2d(1,32,filter_len,stride=2)
		self.conv2 = nn.Conv2d(32,64,filter_len,stride=2)
		self.conv3 = nn.Conv2d(64,128,filter_len,stride=2)
		final_layer_size = 128*H*W

		self.l1 = torch.nn.Linear(final_layer_size , 10, bias=True)
		#self.conv4 = nn.ConvTranspose2d(8, 16, 3, stride=2)


	def extract_HW(self, db):
		H = db['img_height']
		W = db['img_width']
		for m in range(3):
			H = (H - filter_len)/2 + 1
			W = (W - filter_len)/2 + 1
		return [H,W]
	def encoder(self, y0):
		y1 = F.relu(self.conv1(y0))
		y2 = F.relu(self.conv2(y1))
		y3 = F.relu(self.conv3(y2))
		return y3

	def forward(self, y0):
		y1 = self.encoder(y0)
		y2 = y1.view(db['batch_size'],-1)
		y3 = self.l1(y2)

		return y3



if __name__ == '__main__':
	face_data = image_datasets(root_dir='../../dataset/faces/')
	data_loader = DataLoader(face_data, batch_size=5, shuffle=True, num_workers=4)
	
	db = {}
	db['img_height'] = 30
	db['img_width'] = 32
	db['batch_size'] = 5

	ckernel_net = cnn_kernel_net(db)

	for idx, data in enumerate(data_loader):
		data = Variable(data.type(torch.FloatTensor), requires_grad=False)

		encoded_data = ckernel_net(data)

		print(data.shape)
		print(encoded_data.shape)




		import pdb; pdb.set_trace()	



#		data, target = Variable(data), Variable(target)
#		optimizer.zero_grad()
#		output = model(data)
#		loss = F.nll_loss(output, target)
#		loss.backward()
#		optimizer.step()
#		if batch_idx % args.log_interval == 0:
#			print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
#				epoch, batch_idx * len(data), len(train_loader.dataset),
#				100. * batch_idx / len(train_loader), loss.data[0]))











#		diff = float(self.input_dim - self.output_dim)/self.depth
#		sn = np.sign(diff)
#		diff = sn*np.floor(np.absolute(diff))
#
#		inFeatures = int(self.input_dim)
#		outFeatures = int(inFeatures - diff)
#		in_out_list = []
#
#		for l in range(1, self.depth+1):
#			if l == self.depth:
#				in_out_list.append((self.output_dim ,inFeatures))
#				lr = 'self.l' + str(l) + ' = torch.nn.Linear(' + str(inFeatures) + ', ' + str(self.output_dim) + ' , bias=True)'
#				exec(lr)
#				exec('self.l' + str(l) + '.activation = "none"')		#softmax, relu, tanh, sigmoid, none
#			else:
#				in_out_list.append((outFeatures, inFeatures))
#				lr = 'self.l' + str(l) + ' = torch.nn.Linear(' + str(inFeatures) + ', ' + str(outFeatures) + ' , bias=True)'
#				exec(lr)
#				exec('self.l' + str(l) + '.activation = "relu"')
#
#			inFeatures = int(outFeatures)
#			outFeatures = int(inFeatures - diff)
#
#		in_out_list.reverse()
#
#		for l, item in enumerate(in_out_list):
#			c = l + self.depth + 1
#			if c == self.depth:
#				lr = 'self.l' + str(c) + ' = torch.nn.Linear(' + str(item[0]) + ', ' + str(item[1]) + ' , bias=True)'
#				exec(lr)
#				exec('self.l' + str(c) + '.activation = "none"')		#softmax, relu, tanh, sigmoid, none
#			else:
#				lr = 'self.l' + str(c) + ' = torch.nn.Linear(' + str(item[0]) + ', ' + str(item[1]) + ' , bias=True)'
#				exec(lr)
#				exec('self.l' + str(c) + '.activation = "relu"')
#
#
#		self.db = db
#		self.learning_rate = learning_rate
#		self.initialize_network()

#	def initialize_network(self):
#		self.criterion = torch.nn.MSELoss(size_average=False)
#
#		for param in self.parameters():
#			if(len(param.data.numpy().shape)) > 1:
#				torch.nn.init.kaiming_normal(param.data , a=0, mode='fan_in')	
#			else:
#				pass
#				#param.data = torch.zeros(param.data.size())
#
#		self.num_of_linear_layers = 0
#		for m in self.children():
#			if type(m) == torch.nn.Linear:
#				self.num_of_linear_layers += 1
#
#
#
#
#	def output_layer(self, y0, layerId, pause=False):
#		if pause: import pdb; pdb.set_trace() 
#		for count, layer in enumerate(self.children(), 1):
#			if count > self.num_of_linear_layers: break;			
#			if count == self.num_of_linear_layers:
#				exec('y_pred = self.l' + str(count) + '(y' + str(count-1) + ')')
#				return y_pred
#			elif count == self.db['kernel_net_depth']:
#				exec('y' + str(count) + ' = self.l' + str(count) + '(y' + str(count-1) + ')')
#			else:
#				#import pdb; pdb.set_trace()
#				exec('y' + str(count) + ' = F.relu(self.l' + str(count) + '(y' + str(count-1) + '))')
#
#			if count == layerId: 
#				exec('output = y' + str(count))
#				return output
#
#		return y_pred
#
#	def gaussian_kernel(self, x):			#Each row is a sample
#		bs = x.shape[0]
#		s = self.sigma
#
#		K = self.db['dataType'](bs, bs)
#		K = Variable(K.type(self.db['dataType']), requires_grad=False)		
#
#		for i in range(bs):
#			for j in range(bs):
#				tmpY = (x[i,:] - x[j,:]).unsqueeze(0)
#				eVal = -(torch.mm(tmpY, tmpY.transpose(0,1)))/(2*s*s)
#				K[i,j] = torch.exp(eVal)
#
#		return K
#
#	def set_ratio(self, ratio):
#		self.beta = torch.from_numpy(np.array([ratio]))
#		self.beta = Variable(self.beta.type(self.db['dataType']), requires_grad=False)
#
#
#	def compute_ratio(self, inputs, labels, indices):
#		xOut = self.forward(inputs)
#		rbk = self.gaussian_kernel(xOut)
#
#		PP = self.Y[indices, :]
#		Ysmall = PP[:, indices]
#		loss = -torch.sum(rbk*Ysmall)
#
#		norm_mag = torch.sum(torch.abs(xOut))		#	L1 regularizer
#		ratio = loss/norm_mag
#
#		return ratio
#
#
#	def set_Y(self, Y_matrix):
#		Y_matrix = torch.from_numpy(Y_matrix)
#		self.Y = Variable(Y_matrix.type(self.db['dataType']), requires_grad=False)
#
#	def get_optimizer(self):
#		return torch.optim.Adam(self.parameters(), lr=self.learning_rate)
#		
#	def pretrain_loss(self, x, label, indices):
#		y_pred = self.forward(x)
#
#		return self.criterion(y_pred, x)
#
#
#	def compute_loss(self, x, label, indices):
#		#noise = 0.1*torch.randn(x.shape)
#		#noise = Variable(noise.type(self.db['dataType']), requires_grad=False)
#		#x = x + noise
#
#		x_out = self.forward(x)
#		rbk = self.gaussian_kernel(x_out)
#
#		#reg = self.criterion(self.y_pred, x)
#		PP = self.Y[indices, :]
#		Ysmall = PP[:, indices]
#		cost = -torch.sum(rbk*Ysmall)
#		#loss = cost + 0.1*reg
#
#		return cost
#
#	def copy_linear_layer_weights(self, other_network):
#		both_nets = zip(self.children() , other_network.children())
#
#		self.original_weights = []
#		for layer in both_nets:
#			if type(layer[0]) != torch.nn.Linear: continue
#
#			layer[0].weight = layer[1].weight
#			layer[0].bias = layer[1].bias
#		
#
#	def forward(self, y0):
#		import pdb; pdb.set_trace()
#		for m, layer in enumerate(self.children(),1):
#			import pdb; pdb.set_trace()
#			if m == self.db['kernel_net_depth']*2:
#				cmd = 'self.y_pred = self.l' + str(m) + '(y' + str(m-1) + ')'
#				exec(cmd)
#				break;
#			elif m == self.db['kernel_net_depth']:
#				var = 'y' + str(m)
#				cmd = var + ' = self.l' + str(m) + '(y' + str(m-1) + ')'
#				exec(cmd)
#
#				#if self.training_mode == 'kernel_net':
#				#	exec('self.fx = y' + str(self.db['kernel_net_depth']))
#				#	break;
#
#			else:
#				var = 'y' + str(m)
#				cmd = var + ' = F.relu(self.l' + str(m) + '(y' + str(m-1) + '))'
#				#cmd2 = var + '= F.dropout(' + var + ', training=self.training)'
#				exec(cmd)
#				#exec(cmd2)
#
#
#		exec('self.fx = y' + str(self.db['kernel_net_depth']))
#
#		if self.training_mode == 'autoencoder': return self.y_pred
#		elif self.training_mode == 'kernel_net': return self.fx
#		else: 
#			print('Error in cnn_kernel_net due to unrecognized training_mode=%s'%self.training_mode)













#import torch
#import torchvision
#from torch import nn
#from torch.autograd import Variable
#from torch.utils.data import DataLoader
#from torchvision import transforms
#from torchvision.utils import save_image
#from torchvision.datasets import MNIST
#import os
#
#if not os.path.exists('./dc_img'):
#	os.mkdir('./dc_img')
#
#
#def to_img(x):
#	x = 0.5 * (x + 1)
#	x = x.clamp(0, 1)
#	x = x.view(x.size(0), 1, 28, 28)
#	return x
#
#
#num_epochs = 100
#batch_size = 128
#learning_rate = 1e-3
#
#img_transform = transforms.Compose([
#	transforms.ToTensor(),
#	transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
#])
#
#dataset = MNIST('./data', transform=img_transform)
#dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
#
#
#class autoencoder(nn.Module):
#	def __init__(self):
#		super(autoencoder, self).__init__()
#		self.encoder = nn.Sequential(
#			nn.Conv2d(1, 16, 3, stride=3, padding=1),  # b, 16, 10, 10
#			nn.ReLU(True),
#			nn.MaxPool2d(2, stride=2),  # b, 16, 5, 5
#			nn.Conv2d(16, 8, 3, stride=2, padding=1),  # b, 8, 3, 3
#			nn.ReLU(True),
#			nn.MaxPool2d(2, stride=1)  # b, 8, 2, 2
#		)
#		self.decoder = nn.Sequential(
#			nn.ConvTranspose2d(8, 16, 3, stride=2),  # b, 16, 5, 5
#			nn.ReLU(True),
#			nn.ConvTranspose2d(16, 8, 5, stride=3, padding=1),  # b, 8, 15, 15
#			nn.ReLU(True),
#			nn.ConvTranspose2d(8, 1, 2, stride=2, padding=1),  # b, 1, 28, 28
#			nn.Tanh()
#		)
#
#	def forward(self, x):
#		x = self.encoder(x)
#		x = self.decoder(x)
#		return x
#
#
#model = autoencoder().cuda()
#criterion = nn.MSELoss()
#optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate,
#							 weight_decay=1e-5)
#
#for epoch in range(num_epochs):
#	for data in dataloader:
#		img, _ = data
#		img = Variable(img).cuda()
#		# ===================forward=====================
#		output = model(img)
#		loss = criterion(output, img)
#		# ===================backward====================
#		optimizer.zero_grad()
#		loss.backward()
#		optimizer.step()
#	# ===================log========================
#	print('epoch [{}/{}], loss:{:.4f}'
#		  .format(epoch+1, num_epochs, loss.data[0]))
#	if epoch % 10 == 0:
#		pic = to_img(output.cpu().data)
#		save_image(pic, './dc_img/image_{}.png'.format(epoch))
#
#torch.save(model.state_dict(), './conv_autoencoder.pth')
#
