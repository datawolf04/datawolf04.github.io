import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

import pandas as pd
from great_tables import GT, style, loc

class idealProjectile:
  '''
  Does the standard Physics 1 treatment of a projectile on earth for a projectile 
  fired from an elevated position
  Inputs:
    vLaunchMag = launch speed in m/s
    vLaunchDir = launch angle measured from horizontal in degrees
    height = elevation of the position in m
  Outputs: (All in SI units)
    tof = time of flight in seconds
    maxX = range of projectile in m
    position = function that calculates vector position as a function of time
    velocity = function that calculates vector velocity as a function of time
    acceleration = function that calculates vector acceleration as a function of time
  '''
  def __init__(self, vLaunchMag, vLaunchDir, height):
    self.v0 = vLaunchMag
    theta = np.pi/180*float(vLaunchDir)
    self.theta = theta
    self.h = height
    self.g = 9.81
    g = self.g
    v0x = vLaunchMag*np.cos(theta)
    v0y = vLaunchMag*np.sin(theta)
    self.tof = (v0y + np.sqrt(v0y**2 + 2*g*height))/g
    self.maxX = v0x * self.tof

  def position(self, t):
    v0, theta, g, h = self.v0, self.theta, self.g, self.h
    v0x = v0*np.cos(theta)
    v0y = v0*np.sin(theta)
    x = v0x * t
    y = h + v0y*t - 1/2 * g * t**2
    return [x,y]
    
  def velocity(self,t):
    v0, theta, g = self.v0, self.theta, self.g
    v0x = v0*np.cos(theta)
    v0y = v0*np.sin(theta)
    vx = v0x
    vy = v0y - g*t
    return [vx,vy]

  def acceleration(self,t):
    return [0,-self.g]

class dragEOM:
  '''
  Equations of motion for projectile system with turbulent drag fired from an elevated position
  Inputs:
    vLaunchMag = launch speed in m/s
    vLaunchDir = launch angle measured from horizontal in degrees
    height = elevation of the position in m
    mass = mass of projectile in kg
    dragCoef = drag coefficient for system in kg/m
  Outputs:
    udot = [xdot, ydot, vxdot, vydot]
    splash = function that returns y coordinate (needed for integration)
  '''
  def __init__(self, vLaunchMag, vLaunchDir, height, mass, dragCoef):
    self.v0 = vLaunchMag
    theta = np.pi/180*float(vLaunchDir)
    self.theta = theta
    self.h = height
    self.g = 9.81
    g = self.g
    self.coef = dragCoef/mass
    v0x = vLaunchMag*np.cos(theta)
    v0y = vLaunchMag*np.sin(theta)
    self.idealTof = (v0y + np.sqrt(v0y**2 + 2*g*height))/g
    self.u0 = [0, height, v0x, v0y]

  def __call__(self,t,u):
    g, coef = self.g, self.coef
    x, y, vx, vy = u
    xdot, ydot = vx, vy
    vxdot = -coef * np.sqrt(vx**2 + vy**2) * vx
    vydot = -g - coef * np.sqrt(vx**2 + vy**2) * vy
    udot = [xdot, ydot, vxdot, vydot]
    return udot

  def splash(self,t,u):
    return u[1]

  splash.terminal = True


class dragProjectile:
  '''
  Equations of motion for projectile system with turbulent drag fired from an elevated position
  Inputs:
    vLaunchMag = launch speed in m/s
    vLaunchDir = launch angle measured from horizontal in degrees
    height = elevation of the position in m
    mass = mass of projectile in kg
    dragCoef = drag coefficient for system in kg/m
  Outputs:
    t = vector of time values where the system is solved
    x, y = vectors of position values matching the time vector above
    vx, vy = vectors of velocity values matching the time vector above
    ax, ay = vectors of acceleration values matching the time vector above
    tof = time of flight 
    maxX = projectile range
  '''
  def __init__(self, vLaunchMag, vLaunchDir, height, mass, dragCoef):
    model = dragEOM(vLaunchMag, vLaunchDir, height, mass, dragCoef)
    tMax = 10 * model.idealTof
    tVals = np.linspace(0,tMax,1000)
    u0 = model.u0
    sol = solve_ivp(model, t_span=[0,tMax], y0 = u0, t_eval=tVals, events=model.splash, dense_output=True)
    self.tof = sol.t_events[0][0]
    self.maxX = sol.y_events[0][0][0]
    self.t = sol.t
    self.x = sol.y[0, :]
    self.y = sol.y[1, :]
    self.vx = sol.y[2, :]
    self.vy = sol.y[3, :]
    udot = model(sol.t, sol.y)
    self.ax = udot[2]
    self.ay = udot[3]

from matplotlib.patches import Rectangle
ghLogo = u"\uf09b"
liLogo = u"\uf08c"
txt = f"{ghLogo} datawolf04 {liLogo} steven-wolf-253b6625a"

def makeTrajectoryPlot(vi,theta,h,m,c):
  iCan = idealProjectile(vi,theta,h)
  rCan = dragProjectile(vi,theta,h,m,c)

  pltTitle = f'Trajectory for vi={vi:.1f} m/s, theta={theta:.0f} deg, m={m:.1f} kg, c={c:.3f} kg/m'
  
  pos = iCan.position
  tM = iCan.tof
  tt = np.linspace(0,tM,100)
  x, y = pos(tt)
  maxY = np.max((np.max(y),np.max(rCan.y)))
  maxX =  1.1* np.max((np.max(x),np.max(rCan.x)))
  fig, ax = plt.subplots(figsize=(8,4))
  
  ax.plot(x,y,'r',label='Vacuum')
  ax.plot(rCan.x,rCan.y,'g',label='Air')
  ax.axis('equal')
  ax.set_xlabel('x (m)')
  ax.set_ylabel('y (m)')
  ax.set_ylim([0,1.1*maxY])
  # Mark the waterline and the cliff
  ax.fill_between([0, maxX],0, -20, color='aqua',alpha=0.2)
  # ax.axhline(0,color='aqua')
  ax.add_patch(Rectangle((-30,-20),30,y[0]+20, color='slategrey'))
  fig.suptitle(pltTitle)
  ax.legend()
  fig.subplots_adjust(right=0.9,bottom=0.25)
  plt.figtext(0.6,0.01, txt,family=['DejaVu Sans','FontAwesome'],fontsize=10)
  plt.show()
    
def plotCannonCurves(vi,theta,h,m,c):
  iCan = idealProjectile(vi,theta,h)
  rCan = dragProjectile(vi,theta,h,m,c)
  
  pos = iCan.position
  vel = iCan.velocity
  acc = iCan.acceleration
  tMaxI = iCan.tof
  timeI = np.linspace(0,tMaxI,100)
  x, y = pos(timeI)
  vx, vy = vel(timeI)
  ax, ay = acc(timeI)

  def rep(comp):
    if isinstance(comp, float) | isinstance(comp, int) :
      comp = np.repeat(comp,len(timeI))
    return(comp)
      
  x, y = rep(x), rep(y)
  vx, vy = rep(vx), rep(vy)
  ax, ay = rep(ax), rep(ay)
  
  pltTitle = f'Cannon fired at {float(theta):.0f} deg'

  fig, axs = plt.subplots(3,2, sharex=True, sharey='row',figsize=(8,10))
  axs[0,0].plot(timeI,x,label='vacuum')
  axs[0,0].plot(rCan.t,rCan.x,label='air')
  axs[0,0].set_ylabel(r'position $(m)$')
  axs[0,0].set_title('x-component')
  axs[0,1].plot(timeI,y,label='vacuum')
  axs[0,1].plot(rCan.t,rCan.y,label='air')
  axs[0,1].set_title('y-component')
  axs[1,0].plot(timeI,vx,label='vacuum')
  axs[1,0].plot(rCan.t,rCan.vx,label='air')
  axs[1,0].set_ylabel(r'velocity $(m/s)$')
  axs[1,1].plot(timeI,vy,label='vacuum')
  axs[1,1].plot(rCan.t,rCan.vy,label='air')
  axs[2,0].plot(timeI,ax,label='vacuum')
  axs[2,0].plot(rCan.t,rCan.ax,label='air')
  axs[2,0].set_ylabel(r'acceleration $(m/s^2)$')
  axs[2,0].set_xlabel(r'time $(s)$')
  axs[2,1].plot(timeI,ay,label='vacuum')
  axs[2,1].plot(rCan.t,rCan.ay,label='air')
  axs[2,1].set_xlabel(r'time $(s)$')
  fig.suptitle(pltTitle)
  for i in range(3):
    for j in range(2):
      axs[i,j].legend()
  plt.figtext(0.6,0.01, txt,family=['DejaVu Sans','FontAwesome'],fontsize=10)
  plt.show()

