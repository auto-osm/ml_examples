#!/usr/bin/env python

import sys
sys.path.append('../pytorch_load_image/')
import torch
from torch.autograd import Variable
import numpy as np
import torch.nn.functional as F
import matplotlib
from img_load import *
from RFF import *
from sklearn import linear_model
import collections
import pickle
import time



np.set_printoptions(precision=4)
np.set_printoptions(threshold=np.nan)
np.set_printoptions(linewidth=300)
np.set_printoptions(suppress=True)


class cnn_kernel_net(torch.nn.Module):
	def __init__(self, db, learning_rate=0.001):
		super(cnn_kernel_net, self).__init__()
		self.db = db
		self.filter_len = 5
		self.num_output_channels = 128
		[H,W] = self.extract_HW(db)

		self.conv1 = nn.Conv2d(1,16,	self.filter_len,stride=2)
		self.conv2 = nn.Conv2d(16,32,	self.filter_len,stride=2)
		self.conv3 = nn.Conv2d(32,self.num_output_channels,	self.filter_len,stride=2)
		final_layer_size = self.num_output_channels*H*W

		self.l1 = torch.nn.Linear(final_layer_size , 10, bias=True)
		self.l2 = torch.nn.Linear(10, final_layer_size , bias=True)
		self.conv4 = nn.ConvTranspose2d(self.num_output_channels, 32, self.filter_len, stride=2)
		self.conv5 = nn.ConvTranspose2d(32, 16, self.filter_len, stride=2)
		self.conv6 = nn.ConvTranspose2d(16, 1, self.filter_len, stride=2)

		self.criterion = torch.nn.MSELoss(size_average=False)
		self.learning_rate = learning_rate
	
		self.initialize()


	def initialize(self):
		for param in self.parameters():
			if(len(param.data.numpy().shape)) > 1:
				torch.nn.init.kaiming_normal(param.data , a=0, mode='fan_in')	
			else:
				param.data = torch.zeros(param.data.size())


	def initialize_RFF(self, db, sigma):
		self.rff = RFF(30000)
		self.rff.manual_init(db['batch_size'], db['output_dim'], sigma, db['dataType'])

	def set_Y(self, Y_matrix):
		Y_matrix = torch.from_numpy(Y_matrix)
		self.Y = Variable(Y_matrix.type(self.db['dataType']), requires_grad=False)

	def get_optimizer(self):
		return torch.optim.Adam(self.parameters(), lr=self.learning_rate)

	def extract_HW(self, db):
		H = db['img_height']
		W = db['img_width']
		for m in range(3):
			H = (H - self.filter_len)/2 + 1
			W = (W - self.filter_len)/2 + 1
		return [H,W]

	def encoder(self, y0):
		y1 = F.relu(self.conv1(y0))
		y2 = F.relu(self.conv2(y1))
		y3 = F.relu(self.conv3(y2))
		return y3

	def CAE_compute_loss(self, y0, indices=None):
		y_pred = self.CAE_forward(y0)

		#print(y0.shape)
		#print(y_pred.shape)
		#import pdb; pdb.set_trace()
		#return torch.sum((y_pred - y0) ** 2)
		return self.criterion(y_pred, y0)

	def CAE_forward(self, y0):
		y1 = self.encoder(y0)
		y2 = y1.view(y0.shape[0],-1)

		y3 = self.l1(y2)
		y4 = F.relu(self.l2(y3))
		y5 = y4.view( y1.size() )

		y6 = F.relu(self.conv4(y5))
		y7 = F.relu(self.conv5(y6))
		y8 = self.conv6(y7)

		return y8

	def gaussian_kernel(self, x):			#Each row is a sample
		bs = x.shape[0]
		s = self.sigma

		if bs < 50:	# Compute raw RBF kernel
			K = self.db['dataType'](bs, bs)
			K = Variable(K.type(self.db['dataType']), requires_grad=False)		
	
			for i in range(bs):
				for j in range(bs):
					tmpY = (x[i,:] - x[j,:]).unsqueeze(0)
					eVal = -(torch.mm(tmpY, tmpY.transpose(0,1)))/(2*s*s)
					K[i,j] = torch.exp(eVal)
		else: # use RFF
			K = self.rff.get_rbf(x, s, True)
			
		return K



	def compute_loss(self, x, indices):
		x_out = self.forward(x)
		rbk = self.gaussian_kernel(x_out)
		
		PP = self.Y[indices, :]
		Ysmall = PP[:, indices]
		cost = -torch.sum(rbk*Ysmall)

#		print rbk
#		print Ysmall
#		print self.db['dataset'].y[indices]
#		print indices
#		import pdb; pdb.set_trace()
		return cost

	def kernel_net_output(self, y0):
		return self.forward(y0)

	def forward(self, y0):
		y1 = self.encoder(y0)
		y2 = y1.view(y0.shape[0],-1)
		y3 = self.l1(y2)
		return y3



if __name__ == '__main__':
	def loss_optimization_printout(epoch, avgLoss, avgGrad, epoc_loop, slope):
			sys.stdout.write("\r\t\t%d/%d, MaxLoss : %f, AvgGra : %f, progress slope : %f" % (epoch, epoc_loop, avgLoss, avgGrad, slope))
			sys.stdout.flush()

	def get_slope(y_axis):
		y_axis = np.array(list(y_axis))
	
	
		n = len(y_axis)
		LR = linear_model.LinearRegression()
		X = np.array(range(n))
		X = X.reshape((n,1))
		y_axis = y_axis.reshape((n,1))
		LR.fit(X, y_axis)
		#print LR.intercept_
		
		return LR.coef_

	def get_loss(ckernel_net, data_loader):
		#	Compute final average loss
		loss_sum = 0
		for idx, data in enumerate(data_loader):
			data = Variable(data.type(dtype), requires_grad=False)
			try:
				loss = ckernel_net.CAE_compute_loss(data)
			except:
				import pdb; pdb.set_trace()
			loss_sum += loss
		
		avgL = loss_sum/idx
		return avgL.cpu().data.numpy()[0]


	start_time = time.time() 

	if torch.cuda.is_available(): dtype = torch.cuda.FloatTensor
	else: dtype = torch.FloatTensor
	exit_loss=0.001
	face_data = image_datasets('../../dataset/faces/', 'face_img')
	data_loader = DataLoader(face_data, batch_size=5, shuffle=True, drop_last=True)
	

	db = {}
	db['img_height'] = 29
	db['img_width'] = 29
	db['batch_size'] = 5

	epoc_loop = 5000

	if torch.cuda.is_available(): ckernel_net = cnn_kernel_net(db).cuda()
	else: ckernel_net = cnn_kernel_net(db)


	learning_rate = 1e-3
	optimizer = torch.optim.Adam(ckernel_net.parameters(), lr=learning_rate, weight_decay=1e-5)
	avgLoss_cue = collections.deque([], 400)


	avgLoss = get_loss(ckernel_net, data_loader)
	print('Starting avg loss %.3f.'%avgLoss)


	for epoch in range(epoc_loop):
		running_avg = []
		running_avg_grad = []

		for idx, data in enumerate(data_loader):
			data = Variable(data.type(dtype), requires_grad=False)
	
			optimizer.zero_grad()
			loss = ckernel_net.CAE_compute_loss(data)
			loss.backward()
			optimizer.step()
	
			grad_norm = 0	
			for param in ckernel_net.parameters():
				grad_norm += param.grad.data.norm()
	
			running_avg_grad.append(grad_norm)
			running_avg.append(loss.data[0])

		maxLoss = np.max(np.array(running_avg))		#/db['num_of_output']
		avgGrad = np.mean(np.array(running_avg_grad))
		avgLoss_cue.append(maxLoss)
		progression_slope = get_slope(avgLoss_cue)

		loss_optimization_printout(epoch, maxLoss, avgGrad, epoc_loop, progression_slope)

		if maxLoss < exit_loss: break;
		if len(avgLoss_cue) > 300 and progression_slope > 0: break;


	avgLoss = get_loss(ckernel_net, data_loader)
	print('\nEnding avg loss %.3f.'%avgLoss)

	try:
		prev_result = pickle.load( open( "face.p", "rb" ) )
	except:
		prev_result = {}
		prev_result['avgLoss'] = 1000000

	if prev_result['avgLoss'] > avgLoss:
		result = {}
		result['avgLoss'] = avgLoss
		result['kernel_net'] = ckernel_net
		pickle.dump( result, open( "face.p", "wb" ) )

	print("\n--- Run Time : %s seconds ---\n" % (time.time() - start_time))



