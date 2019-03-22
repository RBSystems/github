/*
 main.cpp

 Copyright (c) 2014 Terumasa Tadano

 This file is distributed under the terms of the MIT license.
 Please see the file 'LICENCE.txt' in the root directory 
 or http://opensource.org/licenses/mit-license.php for information.
*/

#include "mpi_common.h"
#include <stdlib.h>
#include <iostream>
#include "alamode.h"

using namespace ALM_NS;

int main(int argc, char **argv)
{

    MPI_Init(&argc, &argv);

    ALM *alm = new ALM(argc, argv, MPI_COMM_WORLD);

    delete alm;

    MPI_Finalize();

    return EXIT_SUCCESS;
}
