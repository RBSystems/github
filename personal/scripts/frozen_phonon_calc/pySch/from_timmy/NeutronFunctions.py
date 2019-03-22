# Definition of functions from Book page 25
import numpy
import matplotlib.pyplot as plt
meV=8.065

########################################################################
## Direct formulas Energy
## as function of Q, Lambda, distance & time, temperature
########################################################################

def Energy_Q(Q):
    # E is in meV
    # Q is in reciprocal Angstrom
    return 16.7/meV*Q^2

def Energy_Lambda(Lambda):
    # E is in meV
    # Lambda is in Angstrom
    return 660/meV*(1/Lambda^2)
  
def Energy_distance_time(d,t):
    # E is in meV
    # d is in meters
    # t in in microseconds
    return 42.2E06/meV*(d/t)^2  
    
def Energy_Temperature(T):
    # E is in meV
    # T is in Kelvin
    # This is just E = kT , k Boltzmann constant
    return 0.695/meV*T    

def EnergyVision(Ef,n,di,df):
    ToF=time_Energy_distance(Ef*n**2,di)
    tf=time_Energy_distance(Ef*n**2,df)
    ti=ToF-tf
    return Energy_distance_time(di,ti)-Ef

########################################################################
## Inverted formulas Q, Lambda, distance and time, temperature
## as a function of Energy
########################################################################

def Q_Energy(E):
    # Q is in reciprocal Angstrom
    # E is in meV
    return sqrt(1/16.7*meV*E)
    
    
    
def Lambda_Energy(E):
    # E is in meV
    # Lambda is in Angstrom
    return sqrt(660/meV/E)    
    
    
def Lambda_Distance_time(d,t):
    # E is in meV
    # d is in meters
    # t in in microseconds
    E=Energy_distance_time(d,t)
    return sqrt(660/meV/E)     
    
def time_Energy_distance(E,d):
    # E is in meV
    # d is in meters
    # t in in microseconds
    return sqrt(42.2E06/meV*d^2/E)

def distance_Energy_time(E,t):
    # E is in meV
    # d is in meters
    # t in in microseconds
    return sqrt(meV/42.2E06*t)
    
########################################################################

# Bragg's Law

########################################################################
    
def Lambda_d_theta(d,theta,n):
    # d is the lattice constant in Angstrom
    # theta is the reflection angle in radians
    # n is the order of the reflection
    return 2*d*sin(theta)/n

def Trajectory(Omega,Ef,Theta,Indirect):
    ki=Q_Energy(Omega)
    kf=Q_Energy(Ef)
    if Indirect==true:
        ki=Q_Energy(Omega+Ef)
    else:
        ki=Q_Energy(Ef)
        kf=Q_Energy(Ef-Omega)
    Q=sqrt(ki^2+kf^2-2*ki*kf*cos(Theta))
    return Q
    
    
def meV2ps(E):
    return 4.13567/E
    
    
    
    
def Recoil(E,mass):
    # Q is in reciprocal Angstrom
    # E is in meV
    return sqrt(1/16.7*meV*E*mass)