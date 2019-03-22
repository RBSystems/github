function [vacf]=find_vacf(v_all,M,Nt)
% v_all(:,:,:): all the velocity data
% M: number of "time origins" used in "time average"
% Nt: number of correlation time points
% vacf(:): VACF data
vacf=zeros(Nt,1);
for nt=0:Nt-1
    for m=1:M
        vacf(nt+1,:)=vacf(nt+1,:)+sum(sum(v_all(:,:,m+0).*v_all(:,:,m+nt)));
    end
end
vacf=vacf/vacf(1);

