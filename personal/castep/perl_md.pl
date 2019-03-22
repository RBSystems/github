#!/usr/bin/perl

## Parses CASTEP output files to extract physical data.
## SYNTAX: perl_md.pl <seedname>  --- (sans extension)
## Maff Glover (mjg11), University of York, 24/02/2004.

## Read seedname from the command line.
$seedname = @ARGV[0];
chomp($seedname);

## Open output files.
open_output_files();

## Parse the CASTEP file.
parse_file();

## Close output files.
close_output_files();


###################### SUBROUTINES - utility ############################

sub open_output_files {

    ## Open output files.for writing.
    open( Vfile  , ">$seedname.V"   ) or die ("Cannot open file: $!");
    open( PEfile , ">$seedname.PE"  ) or die ("Cannot open file: $!");
    open( KEfile , ">$seedname.KE"  ) or die ("Cannot open file: $!");
    open( Efile  , ">$seedname.E"   ) or die ("Cannot open file: $!");
    open( Hfile  , ">$seedname.H"   ) or die ("Cannot open file: $!");
    open( Ehfile , ">$seedname.Eh"  ) or die ("Cannot open file: $!");
    open( Tfile  , ">$seedname.T"   ) or die ("Cannot open file: $!");
    open( Pfile  , ">$seedname.P"   ) or die ("Cannot open file: $!");

};

sub close_output_files {

    ## Close output files.
    close(Vfile ) or die ("Cannot close file: $!");
    close(PEfile) or die ("Cannot close file: $!");
    close(KEfile) or die ("Cannot close file: $!");
    close(Efile ) or die ("Cannot close file: $!");
    close(Hfile ) or die ("Cannot close file: $!");
    close(Ehfile) or die ("Cannot close file: $!");
    close(Tfile ) or die ("Cannot close file: $!");
    close(Pfile ) or die ("Cannot close file: $!");

};

##################### SUBROUTINES - functional ########################


sub parse_file {


    ## Open the input file for reading.
    open(CASTEPfile, "$seedname.castep") 
	or die ("Cannot open input file: $!");

    ## Initialise variables.
    $Vcount  = 0;    $PEcount = 0;    $KEcount = 0;
    $Ecount  = 0;    $Hcount  = 0;    $Ehcount = 0;
    $Tcount  = 0;    $Pcount  = 0;
    
    ## Main loop.
    while (my $line = <CASTEPfile>) {
	
	## Remove trailing newline.
	chomp ($line);
	
	## Volume
	if ($line =~ m/volume =/){
	    ## Whitespace character \s --- plus sign says match any one or more of \s.
	    @fields = split( /\s+/ , $line);
            ## Workaround for glitch in CASTEP files.
	    if( $#fields == 6){
		print (Vfile "$Vcount $fields[5] $fields[6]\n");
	    } 
	    else
	    {   
		$fields[4] =~ s/=//;
		print (Vfile "$Vcount $fields[4] $fields[5]\n");
	    };
     	    $Vcount++;
	};

	## Potential energy
	if ($line =~ m/Potential Energy:/){
	    @fields = split( /\s+/ , $line); 
	    print (PEfile "$PEcount $fields[4] $fields[5]\n");
	    $PEcount++;
	};

	## Kinetic energy
	if ($line =~ m/Kinetic   Energy:/){
	    @fields = split( /\s+/ , $line); 
	    print (KEfile "$KEcount @fields[4] @fields[5]\n");
	    $KEcount++;
       	};

	## Total energy
	if ($line =~ m/Total     Energy:/){
	    @fields = split( /\s+/ , $line); 
	    print (Efile "$Ecount @fields[4] @fields[5]\n");
	    $Ecount++;
       	};

	## Enthalpy
	if ($line =~ m/Enthalpy:/){
	    @fields = split( /\s+/ , $line); 
	    print (Hfile "$Hcount @fields[3] @fields[4]\n");
	    $Hcount++;
       	};

	## Hamiltonian energy
	if ($line =~ m/Hamilt    Energy:/){
	    @fields = split( /\s+/ , $line); 
	    print (Ehfile "$Ehcount @fields[4] @fields[5]\n");
	    $Ehcount++;
       	};

	## Temperature
	if ($line =~ m/Temperature:/){
	    @fields = split( /\s+/ , $line); 
	    print (Tfile "$Tcount @fields[3] @fields[4]\n");
	    $Tcount++;
       	};

	## Pressure
	if ($line =~ m!T/=0 Pressure:!){
	    @fields = split( /\s+/ , $line); 
	    print (Pfile "$Pcount @fields[4] @fields[5]\n");
	    $Pcount++;
       	};
	    
    };

    ## Close the input file
    close(CASTEPfile) 
	or die ("Cannot close input file: $!");

};

