#! /bin/bash

# Program: auto compile tools for rmg

log_file=log.compilation

# pre-defined info
comp_user=$USER
comp_time=`date`
comp_domain=$HOSTNAME

# load modules and replace important files
if [[ $comp_domain == *'h2o'* ]]; then
    module load cmake
    module load boost
    module load magma
    if [ -e ~/common/compile_rmg/CMakeFindRootPath.inc ]; then
        cat ~/common/compile_rmg/CMakeFindRootPath.inc > CMakeFindRootPath.inc
    else
        echo -e "CMakeFindRootPath.inc file not found, exit.\n"
        exit 1
    fi
elif [[ $comp_domain == *'titan'* ]]; then
    if [ -e ~/common/compile_rmg/CMakeFindRootPath.inc ]; then
        cat ~/common/compile_rmg/CMakeFindRootPath.inc > CMakeFindRootPath.inc
    else
        echo -e "CMakeFindRootPath.inc file not found, exit.\n"
        exit 1
    fi
    if [ -e ~/common/compile_rmg/cmake/Modules/FindFFTW.cmake ]; then
        cat ~/common/compile_rmg/cmake/Modules/FindFFTW.cmake > cmake/Modules/FindFFTW.cmake
    else
        echo -e "CMakeFindRootPath.inc file not found, exit.\n"
        exit 1
    fi
    if [ -e ~/common/compile_rmg/cmake/Modules/FindLIBSPG.cmake ]; then
        cat ~/common/compile_rmg/cmake/Modules/FindLIBSPG.cmake > cmake/Modules/FindLIBSPG.cmake
    else
        echo -e "CMakeFindRootPath.inc file not found, exit.\n"
        exit 1
    fi
    sed -i 's/project (RMG C CXX Fortran)/project (RMG)/g' CMakeLists.txt
    sed -i '/enable_language(Fortran)/i\set(CMAKE_Fortran_COMPILER "/opt/cray/craype/default/bin/ftn")' CMakeLists.txt
    #cp CMakeLists.txt CMakeLists.txt.old
    #cat CMakeLists.txt.old | sed 's/project (RMG C CXX Fortran)/project (RMG)/g' | sed '20a # only applicable for ORNL Titan, comment it otherwise\set(CMAKE_Fortran_COMPILER "/opt/cray/craype/2.5.5/bin/ftn")' > CMakeLists.txt
elif [[ $comp_domain == *'or-condo'* ]]; then
    module load PE-gnu/1.0
    module load openmpi/1.10.3
    module load cmake
    if [ -e ~/common/compile_rmg/CMakeFindRootPath.inc ]; then
        cat ~/common/compile_rmg/CMakeFindRootPath.inc > CMakeFindRootPath.inc
    else
        echo -e "CMakeFindRootPath.inc file not found, exit.\n"
        exit 1
    fi
    if [ -e ~/common/compile_rmg/cmake/Modules/FindFFTW.cmake ]; then
        cat ~/common/compile_rmg/cmake/Modules/FindFFTW.cmake > cmake/Modules/FindFFTW.cmake
    else
        echo -e "CMakeFindRootPath.inc file not found, exit.\n"
        exit 1
    fi
fi

# remove previous log files
if [ -e $log_file ]; then
    rm $log_file
fi

echo -e "Compiled & built by $comp_user on $comp_domain at $comp_time\n\n" | tee -a $log_file

module list 2>&1 | tee -a $log_file

# cmake step
echo -e '
------------------------------------------------------------
                            CMAKE
------------------------------------------------------------\n' | tee -a $log_file
cmake . 2>&1 | tee -a $log_file

# make step
if [ $? -eq 0 ]; then
    echo -e '\n\n\n\n
------------------------------------------------------------
                            MAKE
------------------------------------------------------------\n' | tee -a $log_file
    make -j 32 rmg-cpu 2>&1 | tee -a $log_file
fi

# copy compiled executable file to binary
if [ $? -eq 0 ]; then
    if [[ $comp_domain == *'h2o'* ]]; then
        cp rmg-cpu ~/bin/
    elif [[ $comp_domain == *'titan'* ]]; then
        echo -e "titan"
    fi
fi

exit 0
