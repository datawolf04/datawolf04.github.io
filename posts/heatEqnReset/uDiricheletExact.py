import numpy as np

# This function computes the solution to the Dirichlet problem for a unit rod
# with boundary conditions u(0,t) = 0 and u(1,t) = 0, and initial condition
# u(x,0) = T0, where T0 is the initial temperature distribution along the rod, and has been 
def uDiricheletExact(t,x,T0):
  '''
  Computes the exact solution to the Dirichlet problem for a unit rod at time t 
  and position x assuming a uniform initial temperature T0.
  '''
  # The answer is a Fourier series solution of the form:
  # u(x,t) = sum_{n=0}^{\infty} uD
  def uD(n):
    return 4*T0/((2*n+1)*np.pi) * np.sin((2*n+1)*np.pi*x) * np.exp(-(2*n+1)**2 * np.pi**2 * t)
  # Evaluate the sum from n=0 to positive infinity
  uDiricheletExact = 0
  for n in range(1000):  # Using a finite number of terms for practical computation
    uDiricheletExact += uD(n)
  # Return the computed solution
  return uDiricheletExact