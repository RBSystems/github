#phonopy -d --dim="3 3 4" -c POSCAR-unitcell
#mv SPOSCAR POSCAR
#rm POSCAR-???
#rm disp.yaml

out=seed
#phonopy --fc vasprun.xml
#phonopy -c POSCAR-unitcell mesh.conf
2climax.py -v POSCAR-unitcell mesh.yaml ${out}.aclimax
oclimax ${out}.aclimax
csv2nxs.py ${out}.csv

