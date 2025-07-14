import numpy as np
import matplotlib.pyplot as plt

class uRobin:
  def __init__(self,T0, N, tMax, Dt, b):
    self.b = b
    h = 1/(N-1)
    self.xi = np.linspace(0,1,N)
    self.tVals = np.arange(0,tMax, Dt)

    A = 2*(1 + 3*Dt*(b+h)/(b*h**2))
    B = 4*(1 + 3*Dt/h**2)
    C = 1 - 6*Dt/h**2

    ## Left hand side
    K = np.zeros([N,N])
    Gsq = np.zeros([N,N])
    for i in range(1,N-1):
      K[i,i] = B
      K[i, i-1] = C
      K[i, i+1] = C
      Gsq[i,i] = 4
      Gsq[i,i-1] = 1
      Gsq[i,i+1] = 1
    
    K[0, 0:2] = [A, C]
    K[N-1, N-2:] = [C, A]
    Gsq[0, 0:2] = [2,1]
    Gsq[N-1, N-2:] = [1,2]

    nSteps = int(tMax/Dt)
    self.U = np.zeros([N,nSteps])
    G = np.ones(N)
    for k in range(nSteps):
      if(k==0):
        newU = np.ones(N) * T0
      else:
        G = np.matmul(Gsq,oldU)
        newU = np.linalg.solve(K,G)
      self.U[:, k] = newU    
      oldU = newU
  
  def plotTemp(self):
    T, X = np.meshgrid(self.tVals, self.xi)
    fig = plt.figure()
    fig.suptitle(f'Temperature plot for b={self.b:.2f}')
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(T,X,self.U,cmap='magma')
    ax.set_xlabel(r'$t$')
    ax.set_ylabel(r'$x$')
    ax.set_zlabel(r'$u$')
    plt.show()
    
## umatrix(10,101,5,0.02,.5).plotTemp()
