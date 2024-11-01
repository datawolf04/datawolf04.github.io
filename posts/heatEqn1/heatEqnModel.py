import numpy as np
import matplotlib.pyplot as plt


def getIndices(L,W,H,T,Deltax,Deltat):
  xmax = int(L/Deltax)
  ymax = int(W/Deltax)
  zmax = int(H/Deltax)
  tmax = int(T/Deltat)
  
  xmid = xmax // 2
  ymid = ymax // 2
  zmid = zmax // 2
  
  xgrid = np.linspace(0,L,xmax+1)
  ygrid = np.linspace(0,W,ymax+1)
  zgrid = np.linspace(0,H,zmax+1)
  
  out = [L,W,H,T,xmax, ymax, zmax, tmax, xmid, ymid, zmid, xgrid, ygrid, zgrid]
  return out

# Apply BCs at given time step
def applyBC(u, l, vair, vground, beta, betaG):
    tmax, xmax, ymax, zmax = u.shape
    u[l, 0, :, :] = (u[l, 1, :, :] + beta * vair[l])/(1+beta)
    u[l, xmax-1, :, :] = (u[l, xmax-2, :, :] + beta * vair[l])/(1+beta)
    u[l, :, 0, :] = (u[l, :, 1, :] + beta * vair[l])/(1+beta)
    u[l, :, ymax-1, :] = (u[l, :, ymax-2, :] + beta * vair[l])/(1+beta)
    u[l, :, :, 0] = (u[l, :, :, 1] + betaG * vground[l])/(1+betaG)
    u[l, :, :, zmax-1] = (u[l, :, :, zmax-2] + beta * vair[l])/(1+beta)
    
    return u

def calcHeatEqn(u,gamma, vair, vground, beta, betaG):
    tmax, xmax, ymax, zmax = u.shape
    for l in range(0,tmax-1):
        for i in range(1, xmax-1):
            for j in range(1, ymax-1):
                for k in range(1, zmax-1):
                    u[l+1,i,j,k] = u[l,i,j,k] + gamma * (u[l,i+1,j,k] + u[l,i-1,j,k] + u[l,i,j+1,k] + u[l,i,j-1,k] + u[l,i,j,k+1] + u[l,i,j,k-1] - 6 * u[l,i,j,k])
                    
        # Apply BCs
        u = applyBC(u, l+1, vair, vground, beta, betaG)
    
    return u

def plotheatmaps(u,l,i,j,k,Deltat,Deltax,vair,vground):
    Tmin = u.min()
    Tmax = u.max()
    
    xSlice = u[l,i,:,:].transpose()
    ySlice = u[l,:,j,:].transpose()
    zSlice = u[l,:,:,k].transpose()
    
    time = Deltat*l
    tMins = time // 60
    theMinutes = tMins % 60
    
    tHours = tMins // 60
    theDays = tHours // 24
    theHours = tHours % 24
    
    theTime = str(theDays) + " days " + str(theHours) + " hrs "  + str(theMinutes) + " min"

    xC, yC, zC = [Deltax*i, Deltax*j, Deltax*k]
    
    
    fig, (ax0,ax1,ax2) = plt.subplots(ncols=3,width_ratios=[ymax,xmax,xmax],figsize=(15,3))
    
    fig.suptitle(f"Heatbox Temp at {theTime} \n Outdoor Temp = {vair[l]:.2f} C \n Ground Temp = {vground[l]:.0f} C")
    
    im = ax0.pcolormesh(ygrid, zgrid, xSlice, shading="flat", vmin = Tmin, vmax = Tmax)
    ax0.set_aspect(1)
    ax0.set_title(f"x = {xC:.3f} m")
    ax0.set_xlabel("y")
    ax0.set_ylabel("z")
    fig.colorbar(im, ax = ax0)
    
    ax1.pcolormesh(xgrid, zgrid, ySlice, shading="flat", vmin = Tmin, vmax = Tmax)
    ax1.set_aspect(1)
    ax1.set_title(f"y = {yC:.3f} m")
    ax1.set_xlabel("x")
    ax1.set_ylabel("z")
    fig.colorbar(im, ax = ax1)
    
    ax2.pcolormesh(xgrid, ygrid, zSlice, shading="flat", vmin = Tmin, vmax = Tmax)
    ax2.set_aspect(1)
    ax2.set_title(f"z = {zC:.3f} m")
    ax2.set_xlabel("x")
    ax2.set_ylabel("y")
    fig.colorbar(im, ax = ax2)
    
    fig.tight_layout()
