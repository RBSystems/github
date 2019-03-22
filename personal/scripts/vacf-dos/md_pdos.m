function [vacf,pdos]=md_pdos(D,n0,nxyz,a,pbc,Ne,Np,Nc,Ns,omega,rc,dt,T)
% My unit system: energy-eV; length-Angstrom; mass-atomic mass unit
% D: dimension, which should be 3
% n0: number of atoms in a cubic unit cell, which is 4 in this case
% nxyz(1,3): nxyz(d) is the number of unit cells in the d-th direction
% a(1,3): a(d) is the lattice constant in the d-th direction
% pbc(1,3): pbc(d)=1(0) means periodic (free) in the d-th direction
% Ne: number of time steps in the equilibration stage
% Np: number of time steps in the production stage
% Nc: number of time steps for correlation in the production stage
% Ns: sampling interval
% omega(:): phonon frequencies to be considered, in units of 1/ps
% rc: cutoff distance
% dt: time step of integration in units of fs
% T: temperature prescribed in units of K
% vacf: velocity auto-correlation function to be calculated
% pdos: phonon density of states to be calculated
K_B=8.625e-5; % Boltzmann's constant in my unit system  
TIME_UNIT_CONVERSION=10.18; % from fs to my unit system
N=n0*nxyz(1)*nxyz(2)*nxyz(3); % number of atoms
L=a.*nxyz; % box size (Angstrom)
dt=dt/TIME_UNIT_CONVERSION; % time step in my unit system
m=ones(N,1)*40; % mass for Argon atom in my unit system
r=initialize_position(N,D,n0,nxyz,a); % initial positions
v=initialize_velocity(K_B,N,D,T,m); % initial velocities
[NN,NL]=find_neighbor(N,L,pbc,rc,r); % fixed neighbor list
[f]=find_force_vectorized(N,D,NN,NL,L,pbc,r); % initial forces
v_all=zeros(N,3,Np/Ns); % All the velocity data to be computed
for step=1:(Ne+Np) % time-evolution started
    for d=1:D % step 1 of Velocity-Verlet
        v(:,d)=v(:,d)+(f(:,d)./m)*(dt*0.5); 
        r(:,d)=r(:,d)+v(:,d)*dt; 
    end
    [f]=find_force_vectorized(N,D,NN,NL,L,pbc,r); % update forces
    for d=1:D % step 2 of Velocity-Verlet
        v(:,d)=v(:,d)+(f(:,d)./m)*(dt*0.5);
    end 
    if step<=Ne; % control temperature in the equilibration stage
        v=v*sqrt(T*D*K_B*N/sum(m.*sum(v.^2,2))); % scale velocity
    elseif mod(step,Ns)==0 % measure in the production stage
        v_all(:,:,(step-Ne)/Ns)=v; % collect all the velocity data
    end
end % time-evolution completed
[vacf]=find_vacf(v_all,(Np-Nc)/Ns,Nc/Ns); % normalized VACF
delta_t=dt*Ns*TIME_UNIT_CONVERSION/1000; % in units of ps
[pdos]=find_pdos(vacf,omega,Nc/Ns,delta_t);


