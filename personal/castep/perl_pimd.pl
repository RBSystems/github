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
    open( PEfile , ">$seedname.PE"  ) or die ("Cannot open file: $!\n");
    open( KEfile , ">$seedname.KE"  ) or die ("Cannot open file: $!\n");
    open( Efile  , ">$seedname.E"   ) or die ("Cannot open file: $!\n");
    open( Hfile  , ">$seedname.H"   ) or die ("Cannot open file: $!\n");
    open( Tfile  , ">$seedname.T"   ) or die ("Cannot open file: $!\n");
    open( Pfile  , ">$seedname.P"   ) or die ("Cannot open file: $!\n");
    open( SEfile , ">$seedname.SE"  ) or die ("Cannot open file: $!\n");

};

sub close_output_files {

    ## Close output files.
    close(PEfile) or die ("Cannot close file: $!\n");
    close(KEfile) or die ("Cannot close file: $!\n");
    close(Efile ) or die ("Cannot close file: $!\n");
    close(Hfile ) or die ("Cannot close file: $!\n");
    close(Tfile ) or die ("Cannot close file: $!\n");
    close(Pfile ) or die ("Cannot close file: $!\n");
    close(SEfile) or die ("Cannot close file: $!\n");

};

##################### SUBROUTINES - functional ########################


sub parse_file {


    ## Open the input file for reading.
    open(CASTEPfile, "$seedname.castep") 
	or die ("Cannot open input file: $!");

    ## Initialise variables.
    $SEcount  = 0;   $PEcount = 0;    $KEcount = 0;
    $Ecount  = 0;    $Hcount  = 0;
    $Tcount  = 0;    $Pcount  = 0;
    
    ## Main loop.
    while (my $line = <CASTEPfile>) {
	
	## Remove trailing newline.
	chomp ($line);
	
	## Potential energy
	if ($line =~ m/Potential Energy:/ && $line =~ m/<-PI/){
	    @fields = split( /\s+/ , $line); 
	    print (PEfile "$PEcount $fields[4]\n");
	    $PEcount++;
	};

	## Kinetic energy
	if ($line =~ m/Kinetic   Energy:/ && $line =~ m/<-PI/){
	    @fields = split( /\s+/ , $line); 
	    print (KEfile "$KEcount $fields[4]\n");
	    $KEcount++;
       	};

	## Total energy
	if ($line =~ m/Total     Energy:/ && $line =~ m/<-PI/){
	    @fields = split( /\s+/ , $line); 
	    print (Efile "$Ecount $fields[4]\n");
	    $Ecount++;
       	};

	## Hamiltonian energy
	if ($line =~ m/Hamilt    Energy:/ && $line =~ m/<-PI/){
	    @fields = split( /\s+/ , $line); 
	    print (Hfile "$Hcount $fields[4]\n");
	    $Hcount++;
       	};

	## Spring energy
	if ($line =~ m/Spring    Energy:/ && $line =~ m/<-PI/){
	    @fields = split( /\s+/ , $line); 
	    print (SEfile "$SEcount $fields[4]\n");
	    $SEcount++;
       	};	

	## Temperature
	if ($line =~ m/Temperature:/ && $line =~ m/<-PI/){
	    @fields = split( /\s+/ , $line); 
	    print (Tfile "$Tcount $fields[3]\n");
	    $Tcount++;
       	};

	## Pressure
	if ($line =~ m!T/=0 Pressure:! && $line =~ m/<-PI/){
	    @fields = split( /\s+/ , $line); 
	    print (Pfile "$Pcount $fields[4]\n");
	    $Pcount++;
       	};
	    
    };

    ## Close the input file
    close(CASTEPfile) 
	or die ("Cannot close input file: $!");

};

