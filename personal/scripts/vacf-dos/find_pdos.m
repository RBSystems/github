function [pdos]=find_pdos(vacf,omega,Nt,delta_t)
% vacf(:): VACF
% omega: phonon angular frequency in units of ps^{-1}
% Nt: number of correlation time points
% delta_t: time interval between two measurements, in units of ps
% pdos(:): PDOS
vacf=vacf.'.*(cos(pi*(0:Nt-1)/Nt)+1)*0.5; % apply a window function
vacf=vacf.*[1,2*ones(1,Nt-1)]/pi; % C(t)=C(-t) and there is only one C(0)
pdos=zeros(length(omega),1); % phonon density of states
for n=1:length(omega) % Discrete cosine transformation
    pdos(n)=delta_t*sum(vacf.*cos(omega(n)*(0:Nt-1)*delta_t));
end


