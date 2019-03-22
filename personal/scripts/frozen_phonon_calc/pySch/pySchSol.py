#!/usr/bin/env python
'''
    Schrodinger equation solver
    input:
        equation or PES file
    output:
        eigenvalues with wavefunctions
    usage:
        python *py <-i filename>
'''

import os
import sys
import yaml
import matplotlib.pyplot as plt
from matplotlib import animation as anim
import numpy as np


# band 8: omega = 56.45158 meV

ver=sys.version_info.major
if ver==2:
    from utils import *
elif ver==3:
    from utils3 import *
else:
    print("Python version not recognized. Python 2.5 or greater required.")


# target atom: hydrogen, which atom to be used to calculate freq
target_atom_id = 3
mass_target = 1.008
mass_total = 137.327*2 + mass_target*4
vector_target = 0.7035733 # amplitude of target polar vector
#vector_target = 0.6817265 # for band 18


# detect the percantage of energy of the targeted atoms
# remember: E is proportional to m*x**2


# 13.6499329661 THz = 56.45158 meV
#read YAML file
yamlfile = "fdm.yaml"
yamlout = yaml.load(open(yamlfile))

atoms = yamlout['atoms']

# read freq & eigvec at Gamma point
for i in range(len(yamlout['phonon'])):
    if np.linalg.norm(yamlout['phonon'][i]['q-position']) < 1.0e-6:
        index_gamma = i
        break

phonon = yamlout['phonon'][index_gamma]
eigvec = []
for i in range(len(phonon['band'])):
    eigvec.append([])
    for j in range(len(yamlout['atoms'])):
        eigvec[-1].append([])
        eigvec[-1][-1].append(phonon['band'][i]['eigenvector'][j][0][0])
        eigvec[-1][-1].append(phonon['band'][i]['eigenvector'][j][1][0])
        eigvec[-1][-1].append(phonon['band'][i]['eigenvector'][j][2][0])

target_band = 8
mass = [ atoms[i]['mass'] for i in range(len(atoms))]
target_eigvec = eigvec[target_band-1]
#target_eigvec = phonon['band'][target_band]['eigenvector']

eigvec_norm = np.linalg.norm(target_eigvec, axis=1)
#??? polar vector is actually prop to sqrt(m)*x
#eng_frac =  mass[target_atom_id]*eigvec_norm[target_atom_id]**2/np.sum(mass*eigvec_norm**2)
eng_frac =  eigvec_norm[target_atom_id]**2


# atomic units
ev2hartree = 0.0367493
angstrom2bohr = 1.8897259886
hbar=1.0
protoneletronration = 1836.152
hartree2meV=27.2114*1000
#m=10.811*1836.152#mass_target
m=1836.152*mass_target
#set precision of numerical approximation
steps=2000

########
# PARTICLE IN A HARMONIC WELL OF DEPTH (D) WITH A FORCE CONSTANT (omega)
########
Case=8
########
# INPUT
########
# set force constant and depth of harmonic well
W=20.0 # this value must be between 0.3 and 1.4
D=0.21
########
# CODE
########
# divide by two so a well from -W to W is of input width
W=W/2.0
# create x-vector from -A to A
xvec=np.linspace(-W,W,steps,dtype=np.float_)
# get step size
h=xvec[1]-xvec[0]
# create the potential from harmonic potential function
#poly_params = eng_frac*ev2hartree*np.array([0.03143982/(angstrom2bohr*eigvec_norm[target_atom_id])**6, 0.14209309/(angstrom2bohr*eigvec_norm[target_atom_id])**4, 0.28702212/(angstrom2bohr*eigvec_norm[target_atom_id])**2])
#poly_params = [0.5*690.3*ev2hartree/angstrom2bohr**4, 0.5*9.4*ev2hartree/angstrom2bohr**2]
#poly_params = [2.38340817e-05,   4.60526456e-04,   1.12784727e-03]
#poly_params = [  4.38893940e-05,   3.50645945e-04,   1.25206704e-03]
#poly_params = [ 0.00010354,  0.0008272 ,  0.0029537 ]
#poly_params = [  9.95593416e-05,   7.89097575e-04,   2.79530337e-03]
#poly_params = [ 0.00010604,  0.00084048,  0.00297733]
poly_params = [  8.82791827e-05,   8.04679255e-04,   2.91845978e-03]
#poly_params = [ -8.42667925e-05,   1.66354049e-03,   1.68146210e-02] # for band 18
U=polynomial_potential(xvec, poly_params, D)
# create Laplacian via 3-point finite-difference method
Laplacian=(-2.0*np.diag(np.ones(steps))+np.diag(np.ones(steps-1),1)\
    +np.diag(np.ones(steps-1),-1))/(float)(h**2)
# create the Hamiltonian
Hamiltonian=np.zeros((steps,steps))
[i,j] = np.indices(Hamiltonian.shape)
Hamiltonian[i==j]=U
Hamiltonian+=(-0.5)*((hbar**2)/m)*Laplacian
# diagonalize the Hamiltonian yielding the wavefunctions and energies
E,V=diagonalize_hamiltonian(Hamiltonian)
# determine theoretical number of energy levels (n)
n=0
while E[n]<0:
    n+=1
#output(Case,['Well width'],[W*2],E,10)
output(Case,['Well width'],[W*2],hartree2meV*(E+D),10)


# create plotfinite_well_plot(E,V,xvec,steps,n,Case,U)
finite_well_plot(E,V,xvec,steps,n,Case,U)
#for i in range(10):
#    print (E[i+1]-E[i])*27000/100/1.5,(E[i+1]-E[0])*27*1e3/100/3

# phonon population calculation
MD_temp = 700
num_wave = 10 # number of waves to be used
meV2Kelvin = 11.604525

V_plot = np.array(zip(*V))

def phpop(omega, MD_temp=300):
    return np.exp(-omega*meV2Kelvin/MD_temp)

# plot superposition probability function
V_plot_norm = []
for i in range(num_wave):
    V_plot_norm.append(V_plot[i]/np.sqrt(np.sum(V_plot[i]**2)))

prob_1 = phpop(hartree2meV*(E[0]+D), MD_temp)
prob_2 = phpop(hartree2meV*(E[1]+D), MD_temp)
#suprob = V_plot_norm[0]**2 + V_plot_norm[1]**2 + 2.0*np.multiply(V_plot_norm[0], V_plot_norm[1])

# plot animation
meV2fs = 4135.66752
fig = plt.figure()
ax = plt.axes(xlim=(0,2000), ylim=(-0.025, 0.025))
#ax = plt.axes(xlim=(0,2), ylim=(-4, 4)) #for animate2
line, = ax.plot([], [], lw=2)
#plt.fill_between([], 0, [])

def init():
    line.set_data([], [])
    return line,

def animate(t):
    x = range(2000)
    y = prob_1*V_plot_norm[0]**2 + prob_2*V_plot_norm[1]**2 + 2.0*np.sqrt(prob_1*prob_2)*np.cos(0.001*t*(E[0]-E[1])*hartree2meV*meV2fs)*np.multiply(V_plot_norm[0], V_plot_norm[1])
    line.set_data(x,y)
    return line,

def animate2(t):
    x = np.linspace(0, 2, 1000)
    y = np.sin(np.pi*x)**2 + np.sin(2.0*np.pi*x)**2 + 2.0*np.cos(0.1*t)*np.sin(np.pi*x)*np.sin(2.0*np.pi*x)
    line.set_data(x,y)
    return line,

#anim = anim.FuncAnimation(fig, animate, init_func=init, frames=5000, interval=200, blit=True); plt.show(); exit()

suprob = prob_1*V_plot_norm[0]**2 + prob_2*V_plot_norm[1]**2 + 2.0*np.sqrt(prob_1*prob_2)*np.multiply(V_plot_norm[0], V_plot_norm[1])
#plt.plot(V_plot_norm[0]**2, label="0")
#plt.plot(V_plot_norm[1]**2, label="1")
plt.plot(suprob, label='all')
plt.legend()
plt.show()
exit()


#prob_dos = phpop(hartree2meV*(E[0]+D))*V_plot[0]**2/np.sum(V_plot[0]**2)
#plt.plot(prob_dos); plt.show(); exit()


prob_dis = [0]*len(V_plot[0])
for i in range(num_wave,-1,-1):
    prob_dis += phpop(hartree2meV*(E[i]+D), MD_temp)*V_plot[i]**2/np.sum(V_plot[i]**2)
    prob_dos = phpop(hartree2meV*(E[i]+D), MD_temp)*V_plot[i]**2/np.sum(V_plot[i]**2)
    plt.plot(prob_dos, label="up to %d"%(i+1))
plt.plot(prob_dis, label="all")
plt.legend()

#plt.plot(prob_dos)
plt.show()
