# build supercells
phonopy --rmg -d -dim="4 4 4" -c unitcell.in
# calculate force sets
#phonopy --rmg -f supercells/supercell-*/*in.00.log
# plot band+dos
#phonopy --rmg -c unitcell.in -s -p band-dos.conf
# plot band only
#phonopy --rmg -c unitcell.in -s -p band.conf
# plot dos only; also needs dos.conf file
#phonopy --rmg -c unitcell.in -s -p mesh.conf
