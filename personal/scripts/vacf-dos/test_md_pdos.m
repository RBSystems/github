clear; close all;

% Input parameters
D=3; % 3-dimensional space
n0=4; % FCC crystal
nxyz=[4,4,4]; % 4 by 4 by 4 
a=5.45*[1,1,1]; % lattice constant for argon (at 80 K)
pbc=[1,1,1]; % periodic in all three directions
Ne=2000; % equilibration, 20 ps
Np=5000;% production, 50 ps
Nc=500; % correlation, 5 ps
Ns=1; % sampling interval
omega=0.05:0.05:20; % in units of 1/ps
rc=10; % cutoff distance
dt=10; % time step in units of fs
T=80; % temperature
correlation_time=(0:Nc/Ns-1)*(Ns*dt); % in units of fs

% Do the MD simulations
tic;
[vacf,pdos]=md_pdos(D,n0,nxyz,a,pbc,Ne,Np,Nc,Ns,omega,rc,dt,T);
toc;

% plotting results

figure;
plot(correlation_time/1000,vacf);
xlabel('Time (ps)','fontsize',20);
ylabel('VACF (normalized)','fontsize',20);
xlim([0,5]);
ylim([-0.6,1]);
set(gca,'fontsize',20,'linewidth',1.5);
set(gca,'ticklength',get(gca,'ticklength')*2);

figure
plot(omega,pdos);
xlabel('\omega (1/ps)','fontsize',20);
ylabel('PDOS (ps)','fontsize',20);
xlim([0,20]);
ylim([0,0.17]);
set(gca,'fontsize',20,'linewidth',1.5);
set(gca,'ticklength',get(gca,'ticklength')*2);

% An important check is that PDOS should be normalized to about 1
normalization_of_pdos=trapz(omega,mean(pdos,2))

