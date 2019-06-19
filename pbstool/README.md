# Program: PBSTOOL
    create and submit pbs files for RMG/qe, etc. save run configurations in separate files
    by zjyx, 2017/02@ORNL

# TODO:
    1. Add self check process when job is done; if anything is wrong, print it out to WARNING

# USAGE:
    pbstool ($pbs.conf file)
    where pbstool should be in system's environment varialbe $PATH, and 
    $pbs.conf is the control file for this script, which should follow the 
    following format:
    -----------------------------------------------------------------------
    # required
    NODES       = 16
    TIME        = 100 20 # in units of hrs, mins
    EXEINPUT    = rmg.in
    EXEPATH     = /home/z8j/bin/rmg-cpu
    THREADS     = 2
    ACCOUNT     = nta108
    
    # optional
    NAME        = surface-pbe221-rlx
    IS_SUBMIT   = true
    QUEUE       = auto
    FORCE_SUB   = false
    EXEOUTPUT   = none
    MODULE      = PrgEnv-gnu
    MODULE      = fftw
    DEPEND      = afterok:1234567
    LINK_DISK   = /mnt/c/scratch/sciteam/zhang7/run pwd Waves

    
    ------------------------------------------------------------------------
    If $pbs.conf is not specified, pbs.conf will be read by default.

    1. if QUEUE is 'debug', then subdirectories will be created and jobs will
       be run in those directories.
    2. if queue is 'auto', queue in pbs will be decided by wall time.
