#! /bin/bash

# Program: auto compile tools for Quantum ESPRESSO

log_file=log.compilation

# pre-defined info
comp_user=$USER
comp_time=`date`
comp_domain=$HOSTNAME

# load modules and replace important files
if [[ $comp_domain == *'h2o'* ]]; then
    module load cmake
    module load boost
    module load hdf5
    if [ -e ~/common/compile_rmg/CMakeFindRootPath.inc ]; then
        cat ~/common/compile_rmg/CMakeFindRootPath.inc > CMakeFindRootPath.inc
    else
        echo -e "CMakeFindRootPath.inc file not found, exit.\n"
        exit 1
    fi
elif [[ $comp_domain == *'titan'* ]]; then
    module swap PrgEnv-pgi PrgEnv-intel
    module load cray-hdf5
    module load fftw
    #sed -i '/enable_language(Fortran)/i\set(CMAKE_Fortran_COMPILER "/opt/cray/craype/default/bin/ftn")' CMakeLists.txt
    #cp CMakeLists.txt CMakeLists.txt.old
    #cat CMakeLists.txt.old | sed 's/project (RMG C CXX Fortran)/project (RMG)/g' | sed '20a # only applicable for ORNL Titan, comment it otherwise\set(CMAKE_Fortran_COMPILER "/opt/cray/craype/2.5.5/bin/ftn")' > CMakeLists.txt
elif [[ $comp_domain == *'or-condo'* ]]; then
    #module load PE-gnu
    module load PE-intel
    module load cmake/3.6.1
    module load openmpi
    module load mkl
    #module load hdf5-parallel
    module load zlib
    module load fftw
    module load xalt
    #module load gcc
fi

# remove previous log files
if [ -e $log_file ]; then
    rm $log_file
fi

echo -e "
------------------------------------------------------------
Package: Quantume ESPRESSO
Compiled & built by $comp_user on $comp_domain at $comp_time\n
------------------------------------------------------------\n" | tee -a $log_file

module list 2>&1 | tee -a $log_file

# cmake step
echo -e '
------------------------------------------------------------
                         CONFIGURE 
------------------------------------------------------------\n' | tee -a $log_file
#./configure --prefix=`pwd` --enable-openmp --enable-parallel --with-scalapack --with-hdf5 ARCH=crayxt 2>&1 | tee -a $log_file
# OpenMP+MPI, for Cades system
./configure --prefix=`pwd` --enable-openmp --enable-parallel --with-scalapack --with-hdf5 2>&1 | tee -a $log_file
# MPI, for Cades system
#./configure --prefix=`pwd` --enable-openmp=no --enable-parallel --with-scalapack --with-hdf5 2>&1 | tee -a $log_file
#./configure --prefix=`pwd` --enable-openmp --enable-parallel --with-scalapack --with-hdf5 2>&1 | tee -a $log_file
#./configure --prefix=`pwd` --enable-openmp --enable-parallel --with-scalapack --with-hdf5 ARCH=crayxt 2>&1 | tee -a $log_file
# OpenMP+MPI, for blue waters

# based on tutorial from QE
sed -i '/DFLAGS         =/s/$/ -D__IOTK_WORKAROUND1/' make.inc

# make all
if [ $? -eq 0 ]; then
    echo -e '\n\n\n\n
------------------------------------------------------------
                            MAKE
------------------------------------------------------------\n' | tee -a $log_file
    make -j 32 all 2>&1 | tee -a $log_file
fi

# make ph
if [ $? -eq 0 ]; then
    echo -e '\n\n\n\n
------------------------------------------------------------
                          MAKE ph
------------------------------------------------------------\n' | tee -a $log_file
    make -j 32 ph 2>&1 | tee -a $log_file
fi

# make epw
if [ $? -eq 0 ]; then
    echo -e '\n\n\n\n
------------------------------------------------------------
                          MAKE epw
------------------------------------------------------------\n' | tee -a $log_file
    make -j 32 epw 2>&1 | tee -a $log_file
fi

echo -e "\nCompilation done.\n"

exit 0
