#!/usr/bin/perl

my $fscalar;
my $bohr_to_ang = 0.52;

### MAIN PROGRAM

set_constants();
command_line();
open_input_files();

## Open the output file.
open (OUTfile, ">$seed.xyz") 
    or die ("Unable to open output file: $! \n");

## 

##Get next line from all input files.
get_multiline();

##While $line[0] matches any whitespace or any non-whitespace. Will not match either at the END of the file.
##Just a way of knowing when to stop without including a <FILEHANDLE> and hence an implicit read.
while($line[0] =~ m/\s+|\S+/ ){
    
    ##Get next line from all input files.
    get_multiline();
    
    ##If found atomic coordinates ...
    if($line[0] =~ m/<-- R/){

	$product = $atoms*$beads;
	print (OUTfile "$product\n");
	print (OUTfile "comment\n");
	
	until($line[0] !~ m/<-- R/){
	    
	    ## ... do for all input files
	    for ($ifile=0;$ifile<$beads;$ifile++){
		
		@current_fields = parse_line($line[$ifile]);
		$ang_x = $current_fields[2]*$bohr_to_ang;
		$ang_y = $current_fields[3]*$bohr_to_ang;
		$ang_z = $current_fields[4]*$bohr_to_ang;
		print (OUTfile "$current_fields[0] $ang_x $ang_y $ang_z \n");
		
		
#	    print (OUTfile "$line[$ifile]\n");
	    };
	    
	    ## Get next line.
	    get_multiline();
	};
	
    };
};


   
## Close the output file.
close (OUTfile);
	    

close_input_files();

### SUBROUTINES ###


sub set_constants()
{
    $tag="_pimd";
};

sub command_line()
## Reads the command line to obtain the seedname and the number
## of path integral beads in the calculation.
{

    ## Identify keywords:
    ## seed, beads

    @args=@ARGV;
    $num_args = $#args;

    for($iarg=0; $iarg<$num_args; $iarg++){

	if($args[$iarg] =~ "-seed"){
	    $seed = $args[$iarg+1];
	    chomp($seed);
	}

	elsif($args[$iarg] =~ "-beads"){
	    $beads = $args[$iarg+1];
	}

	elsif($args[$iarg] =~ "-atoms"){
	    $atoms = $args[$iarg+1];
	};

    };
};

sub open_input_files()
## Opens all input files.
{

    my $fscalar;

    for($ifile=0; $ifile<$beads; $ifile++){
	
	## Construct the filenames to be opened and make filehandle.
	$bead_tag = sprintf "%3.3d" ,$ifile+1;

	$fname[$ifile]   =  join( '', $seed, $tag, $bead_tag, '.md');
	$fhandle[$ifile] = join( '', $seed, $bead_tag, '_handle');

	## Open the file for reading.
	$fscalar = * {sprintf "%s",$fhandle[$ifile]};
	open( $fscalar, "<$fname[$ifile]")
	    or die ("Unable to open input file $fname[$file]: $!\n");

    };

};
	
sub close_input_files()
## Closes all input files
{
    
    my $fscalar;

    for($ifile=0; $ifile<$beads; $ifile++){
	close($fscalar);
    };
}


sub parse_line()
## 
{

    ## Split argument line into fields.
    $tmpline=@_[O];
    @fields = split(/\s+/,$tmpline );

    ## If first field is pure whitespace, remove it.
    if(@fields[0] !~ m/\S+/) {shift(@fields)};

    return(@fields);

}

sub get_multiline()
## Fills the @line array with lines from each of the input files.
{

    my $fscalar;
    my $ifile;

    for($ifile=0; $ifile<$beads; $ifile++){
        $fscalar = * {sprintf "%s",$fhandle[$ifile]};
	$line[$ifile] = <$fscalar>;
	chomp($line[$ifile]);
    };
}
