/*
 alamode.cpp

 Copyright (c) 2014, 2015, 2016 Terumasa Tadano

 This file is distributed under the terms of the MIT license.
 Please see the file 'LICENCE.txt' in the root directory 
 or http://opensource.org/licenses/mit-license.php for information.
*/

#include "mpi_common.h"
#include <iostream>
#include <iomanip>
#include "interaction.h"
#include "symmetry.h"
#include "input.h"
#include "system.h"
#include "files.h"
#include "memory.h"
#include "timer.h"
#include "fcs.h"
#include "fitting.h"
#include "constraint.h"
#include "timer.h"
#include "writes.h"
#include "patterndisp.h"
#include "version.h"

#ifdef _OPENMP
#include <omp.h>
#endif

using namespace ALM_NS;

ALM::ALM(int narg, char **arg, MPI_Comm comm)
{
    mympi = new MyMPI(this, comm);
    input = new Input(this);

    create_pointers();

    if (mympi->my_rank == 0) {
        std::cout << " +-----------------------------------------------------------------+" << std::endl;
        std::cout << " +                         Program ALM                             +" << std::endl;
        std::cout << " +                             Ver.";
        std::cout << std::setw(7) << ALAMODE_VERSION;
        std::cout << "                         +" << std::endl;
        std::cout << " +-----------------------------------------------------------------+" << std::endl;
        std::cout << std::endl;

        std::cout << std::endl;
        std::cout << " Job started at " << timer->DateAndTime() << std::endl;
        std::cout << " The number of MPI processes: " << mympi->nprocs << std::endl;
#ifdef _OPENMP
        std::cout << " The number of OpenMP threads: " 
            << omp_get_max_threads() << std::endl;
#endif
        std::cout << std::endl;

    //input = new Input(this, narg, arg);
    input->parse_input(narg, arg);
    writes->write_input_vars();
    //initialize();
    }

    mympi->MPI_Bcast_string(input->job_title, 0, MPI_COMM_WORLD);
    mympi->MPI_Bcast_string(mode, 0, MPI_COMM_WORLD);

    if (mode == "fitting") {

        execute_fitting();
        /*fcs->init();
        constraint->setup();
        fitting->fitmain();
        writes->writeall();*/

    } else if (mode == "suggest") {

        execute_suggest();
        /*displace->gen_displacement_pattern();
        writes->write_displacement_pattern();
        */

    } else {
        error->exit("alm", "invalid mode: ", mode.c_str());
    }

    if (mympi->my_rank == 0) {
        std::cout << std::endl << " Job finished at "
            << timer->DateAndTime() << std::endl;
    }
    destroy_pointers();
}

ALM::~ALM()
{
    delete input;
    delete mympi;
}

void ALM::create_pointers()
{
    memory = new Memory(this);
    timer = new Timer(this);
    error = new Error(this);
    system = new System(this);
    symmetry = new Symmetry(this);
    writes = new Writes(this);
    interaction = new Interaction(this);
    fcs = new Fcs(this);
    fitting = new Fitting(this);
    constraint = new Constraint(this);
    files = new Files(this);
    displace = new Displace(this);
}

void ALM::destroy_pointers()
{
    delete memory;
    delete timer;
    delete error;
    delete system;
    delete symmetry;
    delete writes;
    delete interaction;
    delete fcs;
    delete fitting;
    delete constraint;
    delete files;
    delete displace;
}

void ALM::setup_base()
{
    system->setup();
    files->setup();
    symmetry->setup();
    interaction->setup();
}

void ALM::execute_fitting()
{
    if (mympi->my_rank == 0) {
        std::cout << "                      MODE = fitting                         " << std::endl;
        std::cout << "                                                             " << std::endl;

    }

    setup_base();

    fcs->init();
    constraint->setup();
    fitting->fitmain();

    if (mympi->my_rank == 0) {
        writes->writeall();
    }
}
