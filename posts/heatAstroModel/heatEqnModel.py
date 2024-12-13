############################################################
## heatEqnModel.py
##
## To accompany Hot Box visualization post.
############################################################

import numpy as np
from scipy.integrate import solve_ivp

# Heat parameters
thermalDiffusivity = 22.39e-6 # meters^2/s for air
heatTransferCoef = 1 # For a typical metal to air W/m^2K
thermalConductivity = 50 # For a typical metal W/mK
specificHeat = 1000 # for aluminum J/kg K
wallDensity = 3000 # kg/m^3 for aluminum
wallThickness = 0.002 # m
solarIntensity = 1000 # W/m^2

# Length parameters (meters)
L = 3
W = 2
H = 1.5

Deltax = 0.05
xmax = int(L/Deltax)
ymax = int(W/Deltax)
zmax = int(H/Deltax)

xmid = xmax // 2
ymid = ymax // 2
zmid = zmax // 2

xgrid = np.linspace(0,L,xmax+1)
ygrid = np.linspace(0,W,ymax+1)
zgrid = np.linspace(0,H,zmax+1)

u0 = np.empty((xmax,ymax,zmax))

##########################################################################################
# Heat Equation functions describing power generation, boundary conditions, and the laplacian

def bdryConv(umat, Tair, B):

    bdryTemp = np.zeros_like(umat)
    uSurf = np.zeros_like(umat)

    bdryTemp[0,:,:].fill(Tair)
    bdryTemp[:,0,:].fill(Tair)
    bdryTemp[:,:,0].fill(Tair)
    bdryTemp[-1,:,:].fill(Tair)
    bdryTemp[:,-1,:].fill(Tair)
    bdryTemp[:,:,-1].fill(Tair)

    uSurf[0,:,:] = umat[0,:,:]
    uSurf[:,0,:] = umat[:,0,:]
    uSurf[:,:,0] = umat[:,:,0]
    uSurf[-1,:,:] = umat[-1,:,:]
    uSurf[:,-1,:] = umat[:,-1,:]
    uSurf[:,:,-1] = umat[:,:,-1]

    duConvdt = B*(bdryTemp - uSurf)
    return duConvdt    

def lap3DFE(umat,dx):
    lap = np.empty_like(umat)

    # Interior elements:
    lap[1:-1,1:-1,1:-1] = (umat[:-2, 1:-1, 1:-1] + umat[2:, 1:-1, 1:-1] + umat[1:-1, :-2, 1:-1] + 
                           umat[1:-1, 2:, 1:-1] + umat[1:-1,1:-1,:-2] + umat[1:-1,1:-1,2:] - 6*umat[1:-1,1:-1,1:-1]) / dx**2

    # Surface elements:
    lap[0,1:-1,1:-1] = (2* umat[1, 1:-1, 1:-1] + 
                        umat[0, :-2, 1:-1] + umat[0, 2:, 1:-1] + umat[0, 1:-1, :-2] + umat[0, 1:-1, 2:] - 6*umat[0, 1:-1, 1:-1]) / (2*dx**2)
    lap[-1,1:-1,1:-1] = (2* umat[-2, 1:-1, 1:-1] + 
                        umat[-1, :-2, 1:-1] + umat[-1, 2:, 1:-1] + umat[-1, 1:-1, :-2] + umat[-1, 1:-1, 2:] - 6*umat[-1, 1:-1, 1:-1]) / (2*dx**2)
    lap[1:-1,0,1:-1] = (2* umat[1:-1, 1, 1:-1] + 
                        umat[:-2, 0, 1:-1] + umat[2:, 0, 1:-1] + umat[1:-1, 0, :-2] + umat[1:-1, 0, 2:] - 6*umat[1:-1, 0, 1:-1]) / (2*dx**2)
    lap[1:-1,-1,1:-1] = (2* umat[1:-1, -2, 1:-1] + 
                        umat[:-2, -1, 1:-1] + umat[2:, -1, 1:-1] + umat[1:-1, -1, :-2] + umat[1:-1, -1, 2:] - 6*umat[1:-1, -1, 1:-1]) / (2*dx**2)
    lap[1:-1,1:-1,0] = (2* umat[1:-1, 1:-1, 1] + 
                        umat[:-2, 1:-1, 0] + umat[2:, 1:-1, 0] + umat[1:-1, :-2, 0] + umat[1:-1, 2:, 0] - 6*umat[1:-1, 1:-1, 0]) / (2*dx**2)
    lap[1:-1,1:-1,-1] = (2* umat[1:-1, 1:-1, -2] + 
                        umat[:-2, 1:-1, -1] + umat[2:, 1:-1, -1] + umat[1:-1, :-2, -1] + umat[1:-1, 2:, -1] - 6*umat[1:-1, 1:-1, -1]) / (2*dx**2)

    # Edge Elements:
    lap[0,0,1:-1] = (2 * umat[1, 0, 1:-1] + 2 * umat[0, 1, 1:-1] + umat[0, 0, :-2] + umat[0, 0, 2:] - 6*umat[0, 0, 1:-1]) / (4*dx**2)
    lap[0,-1,1:-1] = (2 * umat[1, -1, 1:-1] + 2 * umat[0, -2, 1:-1] + umat[0, -1, :-2] + umat[0, -1, 2:] - 6*umat[0, -1, 1:-1]) / (4*dx**2)
    lap[-1,0,1:-1] = (2 * umat[2, 0, 1:-1] + 2 * umat[-1, 1, 1:-1] + umat[-1, 0, :-2] + umat[-1, 0, 2:] - 6*umat[-1, 0, 1:-1]) / (4*dx**2)
    lap[-1,-1,1:-1] = (2 * umat[2, -1, 1:-1] + 2 * umat[-1, -2, 1:-1] + umat[-1, -1, :-2] + umat[-1, -1, 2:] - 6*umat[-1, -1, 1:-1]) / (4*dx**2)
    lap[0,1:-1,0] = (2 * umat[1, 1:-1, 0] + 2 * umat[0, 1:-1, 1] + umat[0, 2:, 0] + umat[0, :-2, 0] - 6*umat[0, 1:-1, 0]) / (4*dx**2)
    lap[0,1:-1,-1] = (2 * umat[1, 1:-1, -1] + 2 * umat[0, 1:-1, -2] + umat[0, 2:, -1] + umat[0, :-2, -1] - 6*umat[0, 1:-1, -1]) / (4*dx**2)
    lap[-1,1:-1,0] = (2 * umat[-2, 1:-1, 0] + 2 * umat[-1, 1:-1, 1] + umat[-1, 2:, 0] + umat[-1, :-2, 0] - 6*umat[-1, 1:-1, 0]) / (4*dx**2)
    lap[-1,1:-1,-1] = (2 * umat[-2, 1:-1, -1] + 2 * umat[-1, 1:-1, -2] + umat[-1, 2:, -1] + umat[-1, :-2, -1] - 6*umat[-1, 1:-1, -1]) / (4*dx**2)
    lap[1:-1,0,0] = (2 * umat[1:-1, 1, 0] + 2 * umat[1:-1, 0, 1] + umat[:-2, 0, 0] + umat[2:, 0, 0] - 6*umat[1:-1, 0, 0]) / (4*dx**2)
    lap[1:-1,0,-1] = (2 * umat[1:-1, 1, -1] + 2 * umat[1:-1, 0, -2] + umat[:-2, 0, -1] + umat[2:, 0, -1] - 6*umat[1:-1, 0, -1]) / (4*dx**2)
    lap[1:-1,-1,0] = (2 * umat[1:-1, -2, 0] + 2 * umat[1:-1, -1, 1] + umat[:-2, -1, 0] + umat[2:, -1, 0] - 6*umat[1:-1, -1, 0]) / (4*dx**2)
    lap[1:-1,-1,-1] = (2 * umat[1:-1, 2, -1] + 2 * umat[1:-1, -1, -2] + umat[:-2, -1, -1] + umat[2:, -1, -1] - 6*umat[1:-1, -1, -1]) / (4*dx**2)    
    
    # Corner Elements:
    lap[0,0,0] = (umat[1, 0, 0] + umat[0, 1, 0] + umat[0, 0, 1] - 3*umat[0, 0, 0]) / (2*dx**2)
    lap[-1,0,0] = (umat[-2, 0, 0] + umat[-1, 1, 0] + umat[-1, 0, 1] - 3*umat[-1, 0, 0]) / (2*dx**2)
    lap[0,-1,0] = (umat[1, -1, 0] + umat[0, -2, 0] + umat[0, -1, 1] - 3*umat[0, -1, 0]) / (2*dx**2)
    lap[0,0,-1] = (umat[1, 0, -1] + umat[0, 1, -1] + umat[0, 0, -2] - 3*umat[0, 0, -1]) / (2*dx**2)
    lap[0,-1,-1] = (umat[1, -1, -1] + umat[0, -2, -1] + umat[0, -1, -2] - 3*umat[0, -1, -1]) / (2*dx**2)
    lap[-1,0,-1] = (umat[-2, 0, -1] + umat[-1, 1, -1] + umat[-1, 0, -2] - 3*umat[-1, 0, -1]) / (2*dx**2)
    lap[-1,-1,0] = (umat[2, -1, 0] + umat[-1, -2, 0] + umat[-1, -1, 1] - 3*umat[-1, -1, 0]) / (2*dx**2)
    lap[-1,-1,-1] = (umat[-2, -1, -1] + umat[-1, -2, -1] + umat[-1, -1, -2] - 3*umat[-1, -1, -1]) / (2*dx**2)

    return lap

##########################################################################################
# Heat Equation and simulating the system for 10 hours
def dudt(t,u, alpha, intensity, dx, Tair, A, B):
    dudt = alpha*lap3DFE(u,dx) + powerGen(u,intensity, A) + bdryConv(u, Tair, B)
    return dudt

def dudtFlat(t,uflat, alpha, intensity, dx, Tair, A, B):
    u = uflat.reshape(xmax,ymax,zmax)
    return dudt(t,u, alpha, intensity, dx, Tair, A, B).flatten()

def simToyHotBox(A,B,tmax, nt):
    oneHour = 3600
    airTemp = 27
    eqTemp = airTemp + A*solarIntensity/B * L*W/(2*(L*W + L*H + W*H))
    u0.fill(airTemp)
    time = np.arange(0,tmax,nt)
    
    hotBoxSim = solve_ivp(dudtFlat, t_span=[0,10*oneHour], y0=u0.flatten(), t_eval= time, 
                            args=[thermalDiffusivity,solarIntensity,Deltax,airTemp,A,B])

    return hotBoxSim

