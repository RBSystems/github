function [r]=initialize_position(N,D,n0,nxyz,a) % FCC crystal
% D: dimension, which should be 3
% n0: number of atoms in a cubic unit cell, which is 4 in this case
% nxyz(1,3): nxyz(d) is the number of unit cells in the d-th direction
% N: number of atoms in the system, which is n0*nxyz(1)*nxyz(2)*nxyz(3)
% a(1,3): a(d) is the lattice constant in the d-th direction
% r(N,3): r(i,d) is the position of atom i along the d-th direction
r0=[0,0,0;0,0.5,0.5;0.5,0,0.5;0.5,0.5,0];r=zeros(N,D);n=0;
for nx=0:nxyz(1)-1
    for ny=0:nxyz(2)-1
        for nz=0:nxyz(3)-1
            for m=1:n0
                n=n+1;r(n,:)=a.*([nx,ny,nz]+r0(m,:));
            end
        end
    end
end
