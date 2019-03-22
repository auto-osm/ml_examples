#!/usr/bin/env python
# Automatically find the gradient of a function
# Download the package at : https://github.com/HIPS/autograd

import autograd.numpy as np
from autograd import grad

# Define a function Tr(WTA W), we know that gradient = (A+AT)W
def trance_quad(W, A): 
	return np.trace(np.dot(np.dot(np.transpose(W),A), W))


#	Initial setup
n = 5
A = np.random.random((n,n))
W = np.random.random((n,1))



grad_foo = grad(trance_quad)       # Obtain its gradient function
print('Autogen Gradient : ', grad_foo(W,A))
print('Theoretical Gradient : ', np.dot((A+np.transpose(A)), W))

import pdb; pdb.set_trace()

