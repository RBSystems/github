/*
 alamode.h

 Copyright (c) 2014 Terumasa Tadano

 This file is distributed under the terms of the MIT license.
 Please see the file 'LICENCE.txt' in the root directory 
 or http://opensource.org/licenses/mit-license.php for information.
*/

/* Declaration of pointers used in the whole program. */

#pragma once

#ifdef _WIN32
#include <mpi.h>
#else
#include "mpi.h"
#endif

#include <string>

namespace ALM_NS
{
    class ALM
    {
    public:
        class Memory *memory;
        class Input *input;
        class System *system;
        class Interaction *interaction;
        class Fcs *fcs;
        class Symmetry *symmetry;
        class Fitting *fitting;
        class Constraint *constraint;
        class Files *files;
        class Displace *displace;
        class Writes *writes;
        class Error *error;
        class Timer *timer;
        class MyMpi *mympi;
        ALM(int, char **, MPI_Comm);
        ~ALM();
        void create_pointers();
        void destroy_pointers();

        std::string mode;
    };
}
