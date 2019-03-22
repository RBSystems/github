package ceteprouts;
#
# Input and Output routines for processing CASTEP, CETEP and related data files.
# and conversion between molecular file formats.
#
#**********************************************************************
#These utilities are copyright (c) Keith Refson. 1999-2012
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#**********************************************************************

#use strict 'vars';

use Math::Complex;

use POSIX;

use Exporter ();
@ISA = qw(Exporter);

@EXPORT = qw(@ATYPE 
	   ReadPDB ReadCSSR ReadXTL ReadSymm ReadFort15 ReadCetep 
	   ReadCerius ReadCetepAnim ReadCeriusAnim ReadFort13 ReadNewCetep
	   ReadViewmol ReadVASP ReadNewtep ReadNewtepCell  ReadNewtepGeom
           ReadNewtepPhonon ReadShelXL
	   WritePDB WriteExpandedPDB WriteCSSR WriteShelx WriteXTL
	   WriteShak  WriteDCDHeader  WriteDCDTraj WriteXYZ WriteXYZPhon
	   WriteFort15 WriteNewFort15 WriteXSF WriteXSFDen WriteXSFHeader
	   WriteViewmol WriteViewmolTraj WriteGULP WriteMARVIN
	   WriteNewtepCell WriteViewmolFreqs 
	   WriteACMM WriteSgroup WriteKptGen
	   WriteEnd WriteFile NullFunc NoName WriteViewmolBands
	   SuperCell
	   ExpandCell ExpandedCell Expand ReBox ExpandPerturbation
	   ABCtoMAT ABCtoMATrhombz ABCtoMATrotaxis ABCtoMATrot ABCtoMATaxis 
           MATtoABC CartToFrac FracToCart MATtoRHOMBZ
	   ReadNewtepDen Write_Xplor Write_grd);
#
# Regexp for matching a number
my $fnumber = qr/-?(?:\d+\.?\d*|\d*\.?\d+)/o;
my $number  = qr/$fnumber(?:[Ee][+-]?\d{1,3})?/o;
my $nonnumeric = qr/[^\s\d+-.]/o;
#
# Constants
#
my $pi = 3.14159265358979;
my $twopi = 2.0*pi;
my $abohr = 0.529177;
my $hartree=27.2113961;
#
#
#
my $newtep_symmetry = 0;
my $have_cell_constraints = 0;
my @cell_constraints;
my $fix_all_cell;
my $have_external_stress  = 0;
my @external_stress;
my $external_stress_unit;
my %pspfiles;
#
my $ifile;
#
our @ATYPE;
our @SPIN;
#
# The Chemical SYmbols
#    
my
@atsym =  qw(H He Li Be B C N O F Ne Na Mg Al Si P S
             Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn
             Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru
             Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce
             Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu
             Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At
             Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es
             Fm Md No Lr Db Jl Rf Bh Hn Mt);
#
# Atomic Masses
#
my
@atmass = qw(1.00079 4.00260 6.94 9.01218 10.81
             12.011 14.0067 15.9994 18.998403 20.179
             22.98977 24.305 26.98154 28.0855
             30.97376 32.06 35.453 39.948 39.0983
             40.08 44.9559 47.90 50.9415 51.996
             54.9380 55.847 58.9332 58.71 63.546
             65.38 65.735 72.59 74.9216 78.96 79.904
             83.80 85.467 87.62 88.9059 91.22 92.9064
             95.94 98.9062 101.07 102.9055 106.4
             107.868 112.41 114.82 118.69 121.75
             127.60 126.9045 131.30 132.9054 137.33
             138.9055 140.12 140.9077 144.24 145.00
             150.4 151.96 157.25 158.9254 162.50
             164.9304 167.26 168.9342 173.04 174.967
             178.49 180.9479 183.85 186.207 190.2
             192.22 195.09 196.9665 200.59 204.37
             207.2 208.9804 209.0 210.0 222.0 223.0
             226.0254 227.0 232.0381 231.0359 238.029
             237.0482 244.0 243.0 247.0 247.0 251.0
             254.0 257.0 258.0 259.0 260.0 260.0
             260.0 266 261 264 266);
#
# Ususal core charges.
#
my @ichg = qw(1 2 1 2 3 4 5 6 7 8 1 2 3 4 5
             6 7 8 1 2 3 4 5 6 7 8 9 10 11
             2 3 4 5 6 7 8 1 2 3 4 5 6 7 8
             9 10 1 2 3 4 5 6 7 8 1 2 3 4 5
             6 7 8 9 10 11 12 13 14 15 16 3
             4 5 6 7 8 9 10 11 2 3 4 5 6 7
             8 1 2 3 4 5 6 7 8 9 10 11 12
             13 14 15 16 3 4 5 6 7 8 9);
#
#
sub NullFunc {
  1;
}
sub NoName {
   my($junk, $func);
   $junk = shift @_;
   $func = shift @_;
   \&$func(@_);
}
#
# Write an output file for a format defined by the function passed as input
# The output file is one of a sequence and internally numbered.
#
sub WriteFile {
  my ($basename, $func, @args) = @_;
  my $filename;

  #print STDERR "$ifile ";
  $filename = sprintf $basename,$ifile++;
  open STDOUT, ">$filename" or die "Failed to open $filename for writing";
  &$func(@args);
  close STDOUT;
}
#
# Round a number to the nearest multiple of 1/900000 if within 0.45e-7
# of one, otherwise leave alone.  This extends recurring digits.
#

sub round6 {
  my( $num ) = @_;
  
  my($val, $round);
  $val = 900000*$num;
  $round = 10*int(fabs($val/10)+0.5);
  if( $val > 0 && fabs(fabs($val) - $round) < 0.5 ) {
    return int($val+0.5)/900000;
  } elsif( $val < 0 && fabs(fabs($val) - $round) < 0.5 ) {
    return int($val-0.5)/900000;
  } else {
    return $num;
  }
}
#
my $eqtol  = 1.0e-3;  #Tolerance for dimensionless comparisons
my $eqtola = 1.0e-2;  #Tolerance for angle comparison (degrees)
my $eqtoll = 1.0e-3;  #Tolerance for length comparison (fractional, dimensionless)
my $tetra=109.471220634491;

sub same_angle{
  my($aa, $bb) = @_;

  return 1 if fabs($aa - $bb) < $eqtola;
  return 0;
}

sub same_length{
  my($a, $b) = @_;

  my $scale;

  $scale = fabs($a);
  $scale = fabs($b) if fabs($b) > $scale;

  return 1 if fabs(($a - $b)/$scale) < $eqtoll;
  return 0;
}

#
sub ABCtoMAT {
  my ($a, $b, $c, $aa, $ba, $ca, $av, $bv, $cv) = @_;
  my $DTOR = $pi/180.0;

  $caa = cos($aa*$DTOR);
  $cba = cos($ba*$DTOR);
  $cca = cos($ca*$DTOR);

  if( same_length($a,$b) && same_length($a,$c) && same_angle($aa, $ba) && same_angle($aa,$ca) ) {
    if( same_angle($aa,90.0)) {
      &ABCtoMATaxis(@_);
    } elsif( same_angle($aa,60.0)) {
      &ABCtoMATfccprim(@_);
    } elsif( same_angle($aa,109.471220634491)) {
      &ABCtoMATbccprim(@_);
    } else {  
      &ABCtoMATrhombz(@_);
    }
  } elsif (same_length($a,$b) && same_length($a,$c) &&  fabs($caa + $cba + $cca + 1) < $eqtol) {
    &ABCtoMATbcotprim(@_);
  } elsif (same_length($a,$b) && same_angle($aa, $ba)) {
    &ABCtoMATmonoC(@_);
  } elsif (same_length($a,$c) && same_angle($aa, $ca)) {
    &ABCtoMATmonoB(@_);
  } elsif (same_length($b,$c) && same_angle($ba,$ca)) {
    &ABCtoMATmonoA(@_);
  } else {
    &ABCtoMATaxis(@_);
  }
}
#
sub ABCtoMATrot {
  my ($a, $b, $c, $aa, $ba, $ca, $av, $bv, $cv) = @_;

  if( same_length($a,$b) && same_length($a,$c) &&
      same_angle($aa,$ba) && same_angle($aa,$ca)) {
    if( same_angle($aa,90.0)) {
      &ABCtoMATrotaxis(@_);
    } elsif( same_angle($aa,60.0)) {
      &ABCtoMATfccprim(@_);
    } elsif( same_angle($aa,$tetra)) {
      &ABCtoMATbccprim(@_);
    } else {  
      &ABCtoMATrhombz(@_);
    }
  } else {
    &ABCtoMATrotaxis(@_);
  }
}

# Orient a rhombohedral cell as an fcc primitive cell
sub ABCtoMATfccprim {
  my ($a, $b, $c, $aa, $ba, $ca, $av, $bv, $cv) = @_;

  if( same_length($a,$b) && same_length($a,$c) &&
      same_angle($aa,$ba) && same_angle($aa,$ca) &&
      same_angle($aa,60.0) ) {
    $len = sqrt(0.5)*$a;
    @$av = ($len, $len, 0.0   );
    @$bv = ($len, 0.0,    $len);
    @$cv = (0.0,    $len, $len);
  }else {
    die "internal error in  ABCtoMATfccprim: Not an fcc cell";
  }
}

# Orient a rhombohedral cell as a bcc primitive cell
sub ABCtoMATbccprim {
  my ($a, $b, $c, $aa, $ba, $ca, $av, $bv, $cv) = @_;

  my $root3inv = 1.0/sqrt(3.0);

  if( same_length($a,$b) && same_length($a,$c) &&
      same_angle($aa,$ba) && same_angle($aa,$ca) &&
      same_angle($aa,$tetra) ) {
    @$av = ( $root3inv*$a,  $root3inv*$a, -$root3inv*$a   );
    @$bv = ( $root3inv*$a, -$root3inv*$a,  $root3inv*$a);
    @$cv = (-$root3inv*$a,  $root3inv*$a,  $root3inv*$a);
  }else {
    die "internal error in  ABCtoMATbccprim: Not an bcc cell";
  }
}

# Orient a rhombohedral cell with the 3-fold axis along z
sub ABCtoMATrhombz {
  my ($a, $b, $c, $aa, $ba, $ca, $av, $bv, $cv) = @_;
  my ($caa, $saa, $cba, $sba, $cca, $sca, $x, , $z, $root3inv);
  my $DTOR = $pi/180.0;

  $caa = cos($aa*$DTOR); $saa = sin($aa*$DTOR);
  $cba = cos($ba*$DTOR); $sba = sin($ba*$DTOR);
  $cca = cos($ca*$DTOR); $sca = sin($ca*$DTOR);

  $x=sqrt(2.0*(1.0-$cca));
  $z = $a*sqrt(1.0-$x*$x/3.0);
  $x = $a*$x;
  $root3inv=1.0/sqrt(3.0);
  @$av = (      $x*$root3inv,  0.0,    $z);
  @$bv = ( -0.5*$x*$root3inv,  0.5*$x, $z);
  @$cv = ( -0.5*$x*$root3inv, -0.5*$x, $z);
}

sub ABCtoMATaxis {
  my ($a, $b, $c, $aa, $ba, $ca, $av, $bv, $cv) = @_;
  my ($caa, $saa, $cba, $sba, $cca, $sca);
  my $DTOR = $pi/180.0;

  $caa = cos($aa*$DTOR); $saa = sin($aa*$DTOR);
  $cba = cos($ba*$DTOR); $sba = sin($ba*$DTOR);
  $cca = cos($ca*$DTOR); $sca = sin($ca*$DTOR);

  @$cv = (0, 0, $c);
  @$bv = (0, $b * $saa, $b * $caa);
  @$av = ($a / $saa * sqrt(1.0 - $caa*$caa - $cba*$cba - $cca*$cca 
			  + 2.0*$caa*$cba*$cca), 
	  $a / $saa * ($cca - $caa*$cba), $a * $cba);
}
#
#
# Convert cell parameter a,b,c to cell vectors with a along the x axis and b in the xy plane
sub ABCtoMATrotaxis {
  my ($a, $b, $c, $aa, $ba, $ca, $av, $bv, $cv) = @_;
  my ($caa, $saa, $cba, $sba, $cca, $sca);
  my $DTOR = $pi/180.0;

  $caa = cos($aa*$DTOR); $saa = sin($aa*$DTOR);
  $cba = cos($ba*$DTOR); $sba = sin($ba*$DTOR);
  $cca = cos($ca*$DTOR); $sca = sin($ca*$DTOR);

  @$av = ($a, 0, 0);
  @$bv = ($b * $cca, $b * $sca, 0);
  @$cv = ($c * $cba, $c / $sca * ($caa - $cba*$cca),
	  $c / $sca * sqrt(1.0 - $caa*$caa - $cba*$cba - $cca*$cca 
			  + 2.0*$caa*$cba*$cca));
}

# Orient a primitive cell as a bct primitive cell
sub ABCtoMATbcotprim {
  my ($a, $b, $c, $aa, $ba, $ca, $av, $bv, $cv) = @_;

  my ($x1, $x2, $x3);
  my $DTOR = $pi/180.0;
  die "internal error in  ABCtoMATbctprim: Not an bct cell" unless ( same_length($a,$b) && same_length($a,$c));

  $x1 = cos(0.5*$aa*$DTOR) * $a;
  $x2 = cos(0.5*$ba*$DTOR) * $a;
  $x3 = cos(0.5*$ca*$DTOR) * $a;

  @$av = ( -$x1,  $x2,  $x3);
  @$bv = (  $x1, -$x2,  $x3);
  @$cv = (  $x1,  $x2, -$x3);

}
#
# C-centred monoclinic
sub ABCtoMATmonoC {
  my ($a, $b, $c, $aa, $ba, $ca, $av, $bv, $cv) = @_;
  my ($caa, $saa, $cba, $sba, $cca, $sca, $f1);
  my $DTOR = $pi/180.0;

  $cba = cos($ba*$DTOR); $sba = sin($ba*$DTOR);
  $cca2 = cos($ca*$DTOR*0.5); $sca2 = sin($ca*$DTOR*0.5);

  $f1=sqrt(1.0 - ($cba/$cca2)*($cba/$cca2));

  @$av=($a*$cca2, -$a*$sca2,0);
  @$bv=($a*$cca2,  $a*$sca2,0);
  @$cv=($c*$cba/$cca2, 0, $c*$f1);

}
#
# B-centred monoclinic
sub ABCtoMATmonoB {
  my ($a, $b, $c, $aa, $ba, $ca, $av, $bv, $cv) = @_;
  my ($caa, $saa, $cba, $sba, $cca, $sca, $f1);
  my $DTOR = $pi/180.0;

  $caa = cos($aa*$DTOR); $saa = sin($aa*$DTOR);
  $cba2 = cos($ba*$DTOR*0.5); $sba2 = sin($ba*$DTOR*0.5);

  $f1=sqrt(1.0 - ($caa/$cba2)*($caa/$cba2));

  @$av=($a*$cba2, 0, -$a*$sba2);
  @$bv=($b*$caa/$cba2, $b*$f1, 0);
  @$cv=($a*$cba2, 0,  $a*$sba2);

}
#
# A-centred monoclinic
sub ABCtoMATmonoA {
  my ($a, $b, $c, $aa, $ba, $ca, $av, $bv, $cv) = @_;
  my ($caa, $saa, $cba, $sba, $cca, $sca, $f1);
  my $DTOR = $pi/180.0;

  $cca = cos($ca*$DTOR); $sca = sin($ca*$DTOR);
  $caa2 = cos($aa*$DTOR*0.5); $saa2 = sin($aa*$DTOR*0.5);

  $f1=sqrt(1.0 - ($cca/$caa2)*($cca/$caa2));

  @$av=($a*$f1,$a*$cca/$caa2, 0);
  @$bv=(0, $b*$caa2, -$b*$saa2);
  @$cv=(0, $b*$caa2,  $b*$saa2);

}
#
#
sub MATtoRHOMBZ{
  my ($av, $bv, $cv) = @_;
  my ($a, $b, $c, $aa, $ba, $ca) ;

  ($a, $b, $c, $aa, $ba, $ca) = MATtoABC($av, $bv, $cv);
  &ABCtoMATrhombz($a, $b, $c, $aa, $ba, $ca, $av, $bv, $cv);

}

sub MATtoABC {
  my($av, $bv, $cv) = @_;
  my ($a, $b, $c, $aa, $ba, $ca, $ag, $bg, $cg);
  my $RTOD = 180.0 / $pi;

  $a = sqrt($$av[0] ** 2 + $$av[1] ** 2 + $$av[2] ** 2);
  $b = sqrt($$bv[0] ** 2 + $$bv[1] ** 2 + $$bv[2] ** 2);
  $c = sqrt($$cv[0] ** 2 + $$cv[1] ** 2 + $$cv[2] ** 2);
  
  $ag = $RTOD * &acos(($$bv[0] * $$cv[0] + $$bv[1] * $$cv[1] 
		       + $$bv[2] * $$cv[2]) / ($c * $b));
  $bg = $RTOD * &acos(($$av[0] * $$cv[0] + $$av[1] * $$cv[1] 
		       + $$av[2] * $$cv[2]) / ($a * $c));
  $cg = $RTOD * &acos(($$av[0] * $$bv[0] + $$av[1] * $$bv[1] 
		       + $$av[2] * $$bv[2]) / ($a * $b));
  return ($a, $b, $c, $ag, $bg, $cg);
}

sub CellVolume {
    my ($av, $bv, $cv) = @_;
    my ($vol, $astar, $bstar, $cstar);

    @$astar[0]=@$bv[1]*@$cv[2]-@$cv[1]*@$bv[2];
    @$astar[1]=@$bv[2]*@$cv[0]-@$cv[2]*@$bv[0];
    @$astar[2]=@$bv[0]*@$cv[1]-@$cv[0]*@$bv[1];
    @$bstar[0]=@$cv[1]*@$av[2]-@$av[1]*@$cv[2];
    @$bstar[1]=@$cv[2]*@$av[0]-@$av[2]*@$cv[0];
    @$bstar[2]=@$cv[0]*@$av[1]-@$av[0]*@$cv[1];
    @$cstar[0]=@$av[1]*@$bv[2]-@$bv[1]*@$av[2];
    @$cstar[1]=@$av[2]*@$bv[0]-@$bv[2]*@$av[0];
    @$cstar[2]=@$av[0]*@$bv[1]-@$bv[0]*@$av[1];
    $vol=abs(@$av[0]*@$astar[0]+@$av[1]*@$astar[1]+@$av[2]*@$astar[2]);

    return $vol;
}

sub  CheckCellParameters {
   my ( $av, $bv, $cv ) = @_;

   $vol = &CellVolume( $av, $bv, $cv);
   if( $vol <= 0.0 ) {
     $fmt3="%16.10f%16.10f%16.10f\n";
     printf STDERR $fmt3, $$av[0], $$av[1], $$av[2];
     printf STDERR $fmt3, $$bv[0], $$bv[1], $$bv[2];
     printf STDERR $fmt3, $$cv[0], $$cv[1], $$cv[2];
    die "Error reading unit cell parameters: volume ($vol) < 0         ";
  }

}

##sub &CheckCellConstraints {
##  my ($a, $b, $c, $alpha, $beta, $gamma, $cell_constraints) = @_;
##
##  my $symm_tol = 1.0e-7;
##  my ($i, $j);
##
##  for $i (0..5) {
##    $const_map{ $$cell_constraints[$i] } = $i;
##  }
##  
##
##  for $i (0..2) {
##    for $j (3..5) {
##      if( fabs($$cell_constraints[$i] - $$cell_constraints[$i]) < $symm_tol )
##
##  
##}

sub MATinvert {
    my ($av, $bv, $cv, $astar, $bstar, $cstar) = @_;
    my ($bel, $vol);

    @$astar[0]=@$bv[1]*@$cv[2]-@$cv[1]*@$bv[2];
    @$astar[1]=@$bv[2]*@$cv[0]-@$cv[2]*@$bv[0];
    @$astar[2]=@$bv[0]*@$cv[1]-@$cv[0]*@$bv[1];
    @$bstar[0]=@$cv[1]*@$av[2]-@$av[1]*@$cv[2];
    @$bstar[1]=@$cv[2]*@$av[0]-@$av[2]*@$cv[0];
    @$bstar[2]=@$cv[0]*@$av[1]-@$av[0]*@$cv[1];
    @$cstar[0]=@$av[1]*@$bv[2]-@$bv[1]*@$av[2];
    @$cstar[1]=@$av[2]*@$bv[0]-@$bv[2]*@$av[0];
    @$cstar[2]=@$av[0]*@$bv[1]-@$bv[0]*@$av[1];
    $vol=@$av[0]*@$astar[0]+@$av[1]*@$astar[1]+@$av[2]*@$astar[2];
    foreach $bel ((@$astar, @$bstar, @$cstar)) {
	$bel=$bel/$vol;
    }
}

sub CartToFrac {
  my ($av, $bv, $cv, $cartx, $carty, $cartz, $fracx, $fracy, $fracz) = @_;
  my (@astar, @bstar, @cstar);

  my $i;

  MATinvert ($av, $bv, $cv, \@astar, \@bstar, \@cstar);

  for $i (0..$#{$cartx}){
     $$fracx[$i] = $astar[0]*$$cartx[$i] + $astar[1]*$$carty[$i] + $astar[2]*$$cartz[$i];
     $$fracy[$i] = $bstar[0]*$$cartx[$i] + $bstar[1]*$$carty[$i] + $bstar[2]*$$cartz[$i];
     $$fracz[$i] = $cstar[0]*$$cartx[$i] + $cstar[1]*$$carty[$i] + $cstar[2]*$$cartz[$i];
  }
}

sub FracToCartRecip {
  my ($av, $bv, $cv, $fracx, $fracy, $fracz, $cartx, $carty, $cartz) = @_;
  my (@astar, @bstar, @cstar);

  MATinvert ($av, $bv, $cv, \@astar, \@bstar, \@cstar);

  &FracToCart(\@astar, \@bstar, \@cstar, $fracx, $fracy, $fracz, $cartx, $carty, $cartz);
}

sub FracToCart {
  my ($av, $bv, $cv, $fracx, $fracy, $fracz, $cartx, $carty, $cartz ) = @_;
  my ($i);

  if ( ref($fracx) eq "SCALAR" &&  ref($cartx) eq "SCALAR") {
     $$cartx = $$av[0]*$$fracx + $$bv[0]*$$fracy 
                               + $$cv[0]*$$fracz;
     $$carty = $$av[1]*$$fracx + $$bv[1]*$$fracy 
                               + $$cv[1]*$$fracz;
     $$cartz = $$av[2]*$$fracx + $$bv[2]*$$fracy 
                               + $$cv[2]*$$fracz;
  } elsif ( ref($fracx) eq "ARRAY" &&  ref($cartx) eq "ARRAY") {
    for $i (0..$#{$fracx}) {
      $$cartx[$i] = $$av[0]*$$fracx[$i] + $$bv[0]*$$fracy[$i] 
	                                + $$cv[0]*$$fracz[$i];
      $$carty[$i] = $$av[1]*$$fracx[$i] + $$bv[1]*$$fracy[$i] 
                                        + $$cv[1]*$$fracz[$i];
      $$cartz[$i] = $$av[2]*$$fracx[$i] + $$bv[2]*$$fracy[$i] 
                                        + $$cv[2]*$$fracz[$i];
    }
  } else {
    die "FractToCart: Bad call arguments";
  }
}

sub init_atype {
  if ($#ATYPE < 0) {
    $atyp = $ENV{'ATOMS'};
    $atyp = "Mg:O:H:Si" if ($atyp eq '');
    @ATYPE = split(/:/, $atyp, 9999);
    }
}
#
# When presented with a string containing an atomic symbol
# return an integer index into array ATYPE which will look up the symbol.
# Increase size of ATYPE if necessary.
#
sub atom_type{
  my ($asym) = @_;
  my ($i, %indices);
  
  # Make a hash of ATYPE

  for $i (0..$#ATYPE) {
    $indices{$ATYPE[$i]} = $i;
  }

  $asym =~ s/\d+\r?$//;
  unless (exists $indices{$asym}) {
    push @ATYPE,$asym;
    $indices{$asym} = $#ATYPE;
  }

  #print STDERR "atom_type: ",$asym," => ",$indices{$asym},"\n";

  return $indices{$asym};

}

sub atomsyms {
  return @ATYPE;
}

sub ReBox {
    #
    #  Recalculates fractional co-oordinates for a scaled periodic box.
    #  Also rescales cell vectors.
    #
        my ($av, $bv, $cv, $atomx, $atomy, $atomz, $box) = @_;
        my ($x, $ax, $sfac);

        $sfac = $$box[1]-$$box[0];
        foreach $x (@$av) {
            $x *= $sfac;
        }
        foreach $ax (@$atomx) {
            $ax /= $sfac;
        }
        $sfac = $$box[3]-$$box[2];
        foreach $x (@$bv) {
            $x *= $sfac;
        }
        foreach $ax (@$atomy) {
            $ax /= $sfac;
        }
        $sfac = $$box[5]-$$box[4];
        foreach $x (@$cv) {
            $x *= $sfac;
        }
        foreach $ax (@$atomz) {
            $ax /= $sfac;
        }
}
sub TrajCon {
    #
    # Given a set of fractional co-ordinates $atomx,y,z and a
    #  set of previous co-ordinates $atomx,y,zo, adjust $atomx,y,x
    #  to join up trajectories fragmented by periodic boundaries
    #
    my ($atomx, $atomy, $atomz, $atomxo, $atomyo, $atomzo) = @_;
    
    my $i;

    for $i (0..scalar(@$atomx)-1) {
        $$atomx[$i] -= floor($$atomx[$i] - $$atomxo[$i] + 0.5);
        $$atomy[$i] -= floor($$atomy[$i] - $$atomyo[$i] + 0.5);
        $$atomz[$i] -= floor($$atomz[$i] - $$atomzo[$i] + 0.5);
    }
        
}

########################################################################
#
# B E G I N I N G  O F   W R I T E  R O U T I N E S
#
########################################################################
#
# Write a CASTEP fort.15 file.  k-point weight are given in both
# CASTEP and CETEP forms, and file should be readable by either.
#
sub WriteFort15 {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype, $kptx, $kpty, $kptz, $wt ) = @_;
    my ($aty, $i, $fmt3, $fmt4, $fmt4b);
    my @atlist1;
    my @atlist2;

    $fmt3="%16.10f%16.10f%16.10f\n";
    $fmt4="%16.10f%16.10f%16.10f  %5.1f\n";
    $fmt4b="%16.10f%16.10f%16.10f%16.10f\n";
    foreach $i ( (0,1,2,0,1,2) ) {
        printf $fmt3, $$av[$i], $$bv[$i], $$cv[$i];
    }
    #
    # The fort 15 list must be ordered in atom type.
    #  Construct index list sorted by atom type.
    #  N.B.  We also use the index as a secondary sort key as some
    #  sort implementations don't preserve order of equals, and 
    #  the permutation of atoms which results is undesirable.
    #
    @atlist1 = sort {$$atype[$a] <=> $$atype[$b] or $a <=> $b} 0..scalar(@$atype)-1;
    @atlist2 = @atlist1;
    #
    # Loop over atom types printing all atoms of that type. (twice)
    #
    $aty = 0;
    while(scalar(@atlist1) > 0) {
        $aty++;
        while ( scalar(@atlist1) > 0 && $$atype[$atlist1[1]] == $aty ) {
            $i = shift @atlist1;
            printf $fmt4,$$atomx[$i], $$atomy[$i], $$atomz[$i], 1.0;
        }
        while ( scalar(@atlist2) > 0 && $$atype[$atlist2[1]] == $aty ) {
            $i = shift @atlist2;
            printf $fmt3,$$atomx[$i], $$atomy[$i], $$atomz[$i];
        }
    }
    #
    # Write k-points.
    #
    for $i (0..scalar(@$kptx)-1) {
        printf $fmt4b, $$kptx[$i], $$kpty[$i], $$kptz[$i],$$wt[$i];
    }
    for  $i (0..scalar(@$kptx)-1) {
        print $$wt[$i],"\n";
    }

}

#
# Write a "cell.file" for matt Segall's F90 Gamma-point CETEP.
#
sub WriteNewFort15 {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype, $kptx, $kpty, $kptz, $wt ) = @_;
    my ($aty, $i, $fmt3, $fmt4, $fmt4b, $atyp, $nions);
    my (@atlist1, %atno);

    #
    # Create hash to look up atomic numbers from symbols
    #
    @atno{@atsym} = 0..scalar(@atsym)-1;

    #
    # See if the reader stored any ionic species information. If not
    # check the environment variable or use a default.
    #
    init_atype();

    $fmt3="%16.10f%16.10f%16.10f\n";
    $fmt4="%16.10f%16.10f%16.10f  %5.1f\n";
    $fmt4b="%16.10f%16.10f%16.10f%16.10f\n";
    foreach $i ( (0,1,2) ) {
        printf $fmt3, $$av[$i], $$bv[$i], $$cv[$i];
    }
    #
    #  Construct index list sorted by atom type.
    #  N.B.  We also use the index as a secondary sort key as some
    #  sort implementations don't preserve order of equals, and 
    #  the permutation of atoms which results is undesirable.
    #
    @atlist1 = sort {$$atype[$a] <=> $$atype[$b] or $a <=> $b} 0..scalar(@$atype)-1;
    #
    # Loop over atom types printing all atoms of that type. 
    #
    $aty = 0;
    while(scalar(@atlist1) > 0) {
	# Get chemical symbol
        $atyp = $ATYPE[$aty];
        substr ($atyp, 1, 1) =~ tr/[A-Z]/[a-z]/;
        printf "%-12s! Species Symbol\n", $atyp;
	#
        # Look up charge, mass 
	#
        printf "%-12d! Ionic Charge\n", $ichg[$atno{$atyp}];
        printf "%-12g! Mass of species (Atomic units)\n", $atmass[$atno{$atyp}];
	#
	# Count ions of this species
        #
        $nions = scalar(grep $$atype[$_] == $aty, @atlist1);
        printf "%-12d! No. of ions of this species\n", $nions;
        
        while ( scalar(@atlist1) > 0 && $$atype[$atlist1[0]] == $aty ) {
            $i = shift @atlist1;
            printf $fmt4,$$atomx[$i], $$atomy[$i], $$atomz[$i], 1.0;
        }
        $aty++;
    }
    for $i (0..scalar(@$kptx)-1) {
        printf $fmt4b, $$kptx[$i], $$kpty[$i], $$kptz[$i],$$wt[$i];
    }
}

sub acos {
    my($th) = @_;
    atan2(sqrt(1.0 - $th ** 2), $th);
}
#
# Write a SCHAKAL crystal graphics or AVS/CRYSTAL files
#
sub WriteShak {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atyi, $title) = @_;
    my ($a, $b, $c, $ag, $bg, $cg);
    my $iatom;
    my $atyp;

    init_atype();
#
# Do unit cell calculation
#
    ($a, $b, $c, $ag, $bg, $cg) = MATtoABC($av, $bv, $cv);
    print 'CELL ', $a, ' ', $b, ' ', $c, ' ', $ag, ' ', $bg, ' ', $cg, "\n";
#
# Print Atom co-ords
# 
    for $iatom (0..scalar(@$atomx)-1) {
        printf "ATOM  %-4s   %16.13f %16.13f %16.13f\n",$ATYPE[$$atyi[$iatom]],
                $$atomx[$iatom], $$atomy[$iatom],$$atomz[$iatom];
    }
    print "END\n";
}
#
# Write a SHELX crystal structure file
#
sub WriteShelx {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atyi, $title) = @_;
    my ($a, $b, $c, $ag, $bg, $cg);
    my $iatom;

    my $i;
    my $atyp;
    my @atysym;
    my %atyh;

    init_atype();

    $title = "$title  Converted by XX2shx - Keith Refson";
    printf "TITL $title\n";
#
# Do unit cell calculation
#
    ($a, $b, $c, $ag, $bg, $cg) = MATtoABC($av, $bv, $cv);
    printf "CELL  1.54180 %10.7g %10.7g %10.7g %10.7g %10.7g %10.7g\n", $a, $b, $c, $ag, $bg, $cg;
#
# Determine atom types
#
    print "LATT -1\n";
    print "SFAC";
    for $aty (0..$#ATYPE) {
      print " ",$ATYPE[$aty];
    }
    print "\n";
#
# Print Atom co-ords
# 
    for $iatom (0..scalar(@$atomx)-1) {
      $atyp = $ATYPE[$$atyi[$iatom]];
      $atyp =~ s/\d*\s*$//;
#      $atyp = "$atyp$iatom" if( $atyp =~ /^[A-Za-z]{1,2}$/ );
      printf "%-4s %4d  %16.13f %16.13f %16.13f 1.0\n",$atyp, 
                $$atyi[$iatom]+1, $$atomx[$iatom], $$atomy[$iatom],$$atomz[$iatom];
    }

#    print "LATT -1\n";
#    print "SFAC";
#    $i = 0;
#    foreach $atyp (keys %atyh) {
#      $atyh{$atyp} = $i++;
#      print " ",$atyp;
#    }
#    print "\n";
#    
##
## Print Atom co-ords
## 
#    for $iatom (0..scalar(@$atomx)-1) {
#      $atyp = $ATYPE[$$atyi[$iatom]];
#      $atyp =~ s/\d*\s*$//;
##      $atyp = "$atyp$iatom" if( $atyp =~ /^[A-Za-z]{1,2}$/ );
#      printf "%-4s %4d  %16.13f %16.13f %16.13f 1.0\n",$atyp, 
#                $atyh{$atyp}, $$atomx[$iatom], $$atomy[$iatom],$$atomz[$iatom];
#    }
    print "END\n";
}
#
# Write a CSSR (Cambridge Structure Search and Retrieval) file
#
sub WriteCSSR {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atyi, $title) = @_;
    my ($a, $b, $c, $ag, $bg, $cg);
    my $iatom;

    my $atyp;
    my $atomname;

    init_atype();
#
# Do unit cell calculation
#
    ($a, $b, $c, $ag, $bg, $cg) = MATtoABC($av, $bv, $cv);
# Write the cssr header
    printf "%37s %7.3f %7.3f %7.3f\n"," ",$a,$b,$c;
    printf "%21s %7.3f %7.3f %7.3f    SPGR =  1 P 1\n",' ',$ag,$bg,$cg;
    $title = "$title  Converted by XX2CSSR - Keith Refson";
    printf "%4d   0 %60s\n\n", scalar(@$atomx), $title;
#
# Print Atom co-ords
# 
    for $iatom (0..scalar(@$atomx)-1) {
        $atomname = $ATYPE[$$atyi[$iatom]].$iatom;
        printf "%4d %-4s  %9.5f %9.5f %9.5f", $iatom, $atomname, 
                            $$atomx[$iatom], $$atomy[$iatom],$$atomz[$iatom];
        printf "   0   0   0   0   0   0   0   0 %7.3f\n",0.0;
    }
}
#
# Write a Biosym XTL format file
#
sub WriteXTL {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atyi, $title) = @_;
    my ($a, $b, $c, $ag, $bg, $cg);
    my ($iatom, $atomname, $element, $atyp);

    init_atype();
#
# Do unit cell calculation
#
    ($a, $b, $c, $ag, $bg, $cg) = MATtoABC($av, $bv, $cv);
# Write the cssr header

    if( defined($title) ) {
      printf "TITLE %s\n", $title;
    } else {
      printf "TITLE %s\n", "Output from XXX2XTL - Keith Refson";
    }
    printf "DIMENSION 3\n";
    printf "CELL\n %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f\n",$a, $b, $c, $ag, $bg, $cg;
    printf "SYM MAT  1.0  0.0  0.0  0.0  1.0  0.0  0.0  0.0  1.0 0.0000 0.0000 0.0000\n";
    printf "SYMMETRY NUMBER %d\n", 1;
    printf "ATOMS\n";
    printf "NAME       X          Y          Z     CHARGE   TEMP    OCCUP   SCAT\n";
#
# Print Atom co-ords
# 
    for $iatom (0..scalar(@$atomx)-1) {
        $atomname = $ATYPE[$$atyi[$iatom]].($iatom+1);
	$element = $atomname; $element =~ s/[^a-zA-Z]+$//;
	printf "%4s %10.5f %10.5f %10.5f  0.0000  0.0000  1.0000   %2s0+\n",
	  $atomname, $$atomx[$iatom], $$atomy[$iatom],$$atomz[$iatom],$element;
    }
    printf "EOF\n";
}
#
# Write an XYZ format graphics file
#
sub WriteXYZ {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atyi, $title) = @_;
    my ($natoms,$iatom);
    my (@cartx, @carty, @cartz);

    init_atype();

    $natoms = $#{$atomx}+1;
# Write the header

    print "$natoms\n";
    if( defined($title) ) {
      print "$title\n";
    } else {
      print "Output from XXX2XYZ - Keith Refson\n";
    }
#
# Print Atom co-ords
# 
    FracToCart($av, $bv, $cv , $atomx, $atomy, $atomz, 
                              \@cartx, \@carty, \@cartz);
    for $iatom (0..scalar(@cartx)-1) {
        printf "%-8s %7.4f %7.4f %7.4f\n", 
	$ATYPE[$$atyi[$iatom]], $cartx[$iatom], $carty[$iatom], $cartz[$iatom];
    }
}
#
# Write an XYZ format graphics file
#
sub WriteXYZPhon {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atyi, $title, $perta, $pertb, $pertc) = @_;
    my ($natoms,$iatom);
    my (@cartx, @carty, @cartz, @pertx, @perty, @pertz);

    init_atype();

    $natoms = $#{$atomx}+1;
# Write the header

    print "$natoms\n";
    if( defined($title) ) {
      print "$title\n";
    } else {
      print "Output from XXX2XYZ - Keith Refson\n";
    }
#
# Print Atom co-ords
# 
    FracToCart($av, $bv, $cv , $atomx, $atomy, $atomz, 
                              \@cartx, \@carty, \@cartz);
    FracToCart($av, $bv, $cv , $perta, $pertb, $pertc, 
                              \@pertx, \@perty, \@pertz);
    for $iatom (0..scalar(@cartx)-1) {
        printf "%-8s %7.4f %7.4f %7.4f %7.4f %7.4f %7.4f\n", 
	$ATYPE[$$atyi[$iatom]], $cartx[$iatom], $carty[$iatom], $cartz[$iatom],$pertx[$iatom], $perty[$iatom], $pertz[$iatom];
    }
}
#
# Write a GULP input file
#
sub WriteGULP {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atyi, $title,
	$kptx, $kpty, $kptz, $wt, $shells, $spgr) = @_;
    my ($a, $b, $c, $ag, $bg, $cg);
    my $iatom;

    my $atyp;
    my $atomname;

    init_atype();
#
# Do unit cell calculation
#
    ($a, $b, $c, $ag, $bg, $cg) = MATtoABC($av, $bv, $cv);
# Write the  header
     $title = "XX2GULP - Keith Refson" if $title eq "";
    printf "opti prop\ntitle\n%s\nend\n","$title";
    printf "cell\n%7.3f %7.3f %7.3f %7.3f %7.3f %7.3f\n",
      $a,$b,$c,$ag,$bg,$cg;
    printf "frac\n";
#
# Print Atom co-ords
#
    for $iatom (0..scalar(@$atomx)-1) {
      $atomname = $ATYPE[$$atyi[$iatom]];
      printf "%-4s core  %9.5f %9.5f %9.5f\n", $atomname,
	     $$atomx[$iatom], $$atomy[$iatom],$$atomz[$iatom];
      if ($shells ne "" && $atomname =~ $shells ) {
	printf "%-4s shel  %9.5f %9.5f %9.5f\n", $atomname,
	       $$atomx[$iatom], $$atomy[$iatom],$$atomz[$iatom];
      }
    }
    if ( $spgr ne "" ) { 
      printf "space\n$spgr\n";
    }
}
#
# Write a MARVIN restart file
#
sub WriteMARVIN {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atyi, $title,
	$kptx, $kpty, $kptz, $wt, $shells, $r1depth) = @_;
    my ($a, $b, $c, $ag, $bg, $cg);
    my (@cartx, @carty, @cartz);
    my (@avv, @bvv, @cvv);              # Rotated unit cell vectors
    my $iatom;
    my $atyp;
    my $atomname;

    init_atype();
#
# Do unit cell calculation
#
    ($a, $b, $c, $ag, $bg, $cg) = MATtoABC($av, $bv, $cv);
# Write the  header
     $title = "XX2GULP - Keith Refson" if $title eq "";
    printf "# %s\n","$title";

    printf "coordinates 1 A\n";
#
# Print Atom co-ords
#
    # Since unit cell output contains only a,b,c,alpha,beta,gamma,
    # there is an additional unspecified rotation in original unit cell
    # vectors.  We must convert to Cartesians using some convention.
    &ABCtoMATrot($a, $b, $c, $ag, $bg, $cg, \@avv, \@bvv, \@cvv);
    FracToCart(\@avv, \@bvv, \@cvv, $atomx, $atomy, $atomz, 
                              \@cartx, \@carty, \@cartz);

    for $iatom (0..scalar(@$atomx)-1) {
      if ( $$atomz[$iatom] > -$r1depth ) {
	$atomname = $ATYPE[$$atyi[$iatom]];
	printf "%-4s %-4s core  %12.8f %12.8f %12.8f\n", $atomname, $atomname,
	  $cartx[$iatom], $carty[$iatom],$cartz[$iatom];
	if ($shells ne "" && $atomname =~ $shells ) {
	  printf "%-4s %-4s shel  %12.8f %12.8f %12.8f\n", $atomname,$atomname,
	    $cartx[$iatom], $carty[$iatom],$cartz[$iatom];
	}
      }
    }
    printf "end\ncoordinates 2 A\n";
    for $iatom (0..scalar(@$atomx)-1) {
      if ( $cartz[$iatom] <= -$r1depth ) {
	$atomname = $ATYPE[$$atyi[$iatom]];
	printf "%-4s %-4s core  %12.8f %12.8f %12.8f\n", $atomname, $atomname,
	  $cartx[$iatom], $carty[$iatom],$cartz[$iatom];
	if ($shells ne "" && $atomname =~ $shells ) {
	  printf "%-4s %-4s shel  %12.8f %12.8f %12.8f\n", $atomname,$atomname,
	    $cartx[$iatom], $carty[$iatom],$cartz[$iatom];
	}
      }
    }
    printf "end\n";
}
#
# Write a Viewmol file
#
my (@atomxo, @atomyo, @atomzo);
sub WriteViewmol {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atyi, $box, $title, $end) = @_;
    my ($a, $b, $c, $ag, $bg, $cg);
    my (@avv, @bvv, @cvv);              # Rotated unit cell vectors
    my (@cartx, @carty, @cartz,@atomxe,@atomye,@atomze,@atyie);
    my $iatom;
    my $atyp;
    my @shiftlist;

    init_atype();
#
# Do unit cell calculation
#
    ($a, $b, $c, $ag, $bg, $cg) = MATtoABC($av, $bv, $cv);

    print "\$title\n${$title}\n";
    printf "\$unitcell %9.3f%9.3f%9.3f%9.4f%9.4f%9.4f\n",
            $a, $b, $c, $ag, $bg, $cg;
#
# Print Atom co-ords
# 
    my @box=(0,1,0,1,0,1);
    @shiftlist = ExpandedCell ($atomx, $atomy, $atomz, $atyi, \@box);
    Expand($atomx, $atomy, $atomz, $atyi, \@shiftlist,
           \@atomxe, \@atomye, \@atomze, \@atyie);
    print "\$coord  1.0\n";
    #
    # Convert fractional co-ords to Cartesian.
    #
    # Since Viewmol unit cell output contains only a,b,c,alpha,beta,gamma,
    # there is an additional unspecified rotation in original unit cell
    # vectors.  We must convert to Cartesians using Viewmol's comvention.
    &ABCtoMATrot($a, $b, $c, $ag, $bg, $cg, \@avv, \@bvv, \@cvv);
    FracToCart(\@avv, \@bvv, \@cvv, \@atomxe, \@atomye, \@atomze, 
                              \@cartx, \@carty, \@cartz);
    for $iatom (0..scalar(@$atomx)-1) {
      printf "  %12.8f%12.8f%12.8f %s\n", 
             $cartx[$iatom], $carty[$iatom], $cartz[$iatom], 
	     $ATYPE[$$atyi[$iatom]];
    }
    print "\$end\n" if (! $end);
}
sub WriteEnd {
    print "\$end\n";
}
#
# Write the intermediate co-ordinates of a Viewmol file
#
my ($first);
sub WriteViewmolTraj {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atyi, $title, $box, $forcx, $forcy, $forcz, 
        $icycle, $toten, $gnorm) = @_;
    my ($a, $b, $c, $ag, $bg, $cg);
    my (@avv, @bvv, @cvv);              # Rotated unit cell vectors
    my (@cartx, @carty, @cartz);
    my @atyie;
    my $iatom;
    my $atyp;
    my @shiftlist;

    init_atype();
#    print "\$grad          cartesian gradients\n" if ( $first++ == 0);
    print "\$grad\n" if ( $first++ == 0);
#
# Do unit cell calculation
#
    ($a, $b, $c, $ag, $bg, $cg) = MATtoABC($av, $bv, $cv);

    printf "  cycle =%4d    SCF energy =%18.6f   |dE/dxyz| =%10.6f\n",
            $icycle, $toten, $gnorm;
    printf "  unitcell %9.3f%9.3f%9.3f%9.4f%9.4f%9.4f\n",
            $a, $b, $c, $ag, $bg, $cg;

    if (scalar (@atomxo)<= 0) {
      @shiftlist = ExpandedCell ($atomx, $atomy, $atomz, $atyi, $box);
      Expand($atomx, $atomy, $atomz, $atyi, \@shiftlist,
	     \@atomxo, \@atomyo, \@atomzo, \@atyie);
    }
    TrajCon ($atomx, $atomy, $atomz, \@atomxo, \@atomyo, \@atomzo); 
    @atomxo = @$atomx;
    @atomyo = @$atomy;
    @atomzo = @$atomz;
#
# Print Atom co-ords
# 
    # Since Viewmol unit cell output contains only a,b,c,alpha,beta,gamma,
    # there is an additional unspecified rotation in original unit cell
    # vectors.  We must convert to Cartesians using Viewmol's comvention.
    &ABCtoMATrot($a, $b, $c, $ag, $bg, $cg, \@avv, \@bvv, \@cvv);
    FracToCart(\@avv, \@bvv, \@cvv, $atomx, $atomy, $atomz, 
                              \@cartx, \@carty, \@cartz);
    for $iatom (0..scalar(@$atomx)-1) {
      printf "  %12.8f%12.8f%12.8f %s\n", 
             $cartx[$iatom], $carty[$iatom], $cartz[$iatom], 
	     $ATYPE[$$atyi[$iatom]];
    }
    for $iatom (0..scalar(@$atomx)-1) {
        printf "%12.8f%12.8f%12.8f\n", 
                $$forcx[$iatom], $$forcy[$iatom], $$forcz[$iatom];
    }
}
#
# Write the bands to a Viewmol file
#
sub WriteViewmolBands {
  my($nbands, $eigen, $occ) = @_;
  my $iband;

 if ($nbands > 0) {

    print "\$scfmo\n";
    for $iband (0 .. $nbands-1) {
      print $iband," x eigenvalue = ",$$eigen[$iband]/$hartree," nsaos = 0\n"; 
    }
  }
  print "\$end\n";
}
#
# Write the mode frequencies to a Viewmol file
#
sub WriteViewmolFreqs {
  my($freqs,$eigs) = @_;
  my ($iatom,$natoms,$icoord,$iband,$nbands,$nout,$ampr,$ampi,$amp);
  
  
  $nbands = scalar(@$freqs);
  $natoms = $nbands/3;

  print "\$vibrational spectrum\n";
  for $iband (0 .. $nbands-1) {
    print "A1","   ",$$freqs[$iband]," 1.0 1.0\n"
  }

  print "\$vibrational normal modes\n";
  $nout=0;
  printf "   1   1";
  for $iatom (0 .. $natoms-1) {
    for $icoord (0 .. 2) {
      for $iband (0 .. $nbands-1) {
	printf "\n   1   1" if($nout > 0 && $nout%6 == 0);
	$ampr = $$eigs[$iband][$iatom][2*($icoord-1)+1];
	$ampi = $$eigs[$iband][$iatom][$icoord];
	$amp = sqrt($ampr*$ampr + $ampi*$ampi);
	$amp = -$amp if $ampr < 0.0;
	printf "%12.8f", $amp;
	$nout++;
      }
    }
  }
  print "\n";
  print "\$end\n";
}
#
# Write a XCrysden XSF file
#
sub WriteXSF {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atyi, $title, 
	$junk1, $junk2, $junk3, $junk4, $iframe, $junk) = @_;
    my (@cartx, @carty, @cartz,@atomxe,@atomye,@atomze,@atyie);
    my $iatom;
    my $atyp;
    my @shiftlist;

    init_atype();

    print "CRYSTAL\n" if $iframe <=0;
#
# Unit Cell
#
    print "PRIMVEC $iframe\n";
    printf " %16.8f %16.8f %16.8f\n", $$av[0], $$av[1], $$av[2];
    printf " %16.8f %16.8f %16.8f\n", $$bv[0], $$bv[1], $$bv[2];
    printf " %16.8f %16.8f %16.8f\n", $$cv[0], $$cv[1], $$cv[2];
    print "\n\nCONVVEC $iframe\n";
    printf " %16.8f %16.8f %16.8f\n", $$av[0], $$av[1], $$av[2];
    printf " %16.8f %16.8f %16.8f\n", $$bv[0], $$bv[1], $$bv[2];
    printf " %16.8f %16.8f %16.8f\n", $$cv[0], $$cv[1], $$cv[2];
#
# Print Atom co-ords
# 
    #
    # Convert fractional co-ords to Cartesian.
    #
    FracToCart($av, $bv, $cv, $atomx, $atomy, $atomz, 
                              \@cartx, \@carty, \@cartz);
    printf "PRIMCOORD $iframe\n%5d %5d\n", $#{$atomx},1;
    for $iatom (0..scalar(@$atomx)-1) {
      printf "%2s  %12.8f%12.8f%12.8f\n", 
             $ATYPE[$$atyi[$iatom]],$cartx[$iatom], $carty[$iatom], $cartz[$iatom];
    }
}
#
# Write a XCrysden XSF file header - 1st frame for animation
#
sub WriteXSFHeader {
    print "ANIMSTEPS $nframes\n";
    print "CRYSTAL\n";
}
sub CountNewGeomFrames {
  my($count);

  $count = 0;

  while(<>) {
    if( /^\s+\d+$/) {
 #     die "Failed to count frames in geom file ($count):$_" unless  /^\s+$count$/;
      $count++;
    }
  }

  return $count;
}
#
# Write a XCrysden XSF file containing a density
#
sub WriteXSFDen {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atyi, $title, $nx, $ny, $nz, $den) = @_; 
    my (@cartx, @carty, @cartz,@atomxe,@atomye,@atomze,@atyie);
    my $iatom;
    my $atyp;
    my @shiftlist;

    WriteXSF($av, $bv, $cv, $atomx, $atomy, $atomz, $atyi, $title);

use Cwd 'abs_path';
    print "BEGIN_BLOCK_DATAGRID_3D\nDensities\nBEGIN_DATAGRID_3D_Density\n";
    printf " %d %d %d\n",$nz+1,$ny+1,$nx+1;
    printf " %10.6f  %10.6f  %10.6f\n", 0.0,0.0,0.0;
    printf " %10.6f  %10.6f  %10.6f\n", $$cv[0],$$cv[1],$$cv[2];
    printf " %10.6f  %10.6f  %10.6f\n", $$bv[0],$$bv[1],$$bv[2];
    printf " %10.6f  %10.6f  %10.6f\n", $$av[0],$$av[1],$$av[2];
    
    for ($i = 0; $i < $nx+1; $i++) {
      for ($j = 0; $j < $ny+1; $j++) {
	for ($k = 0; $k < $nz+1; $k++) {
	  printf "%12.5f\n",$$den[$i%$nx][$j%$nx][$k%$nz];
	}
	
      }
    }
    print "END_DATAGRID_3D_Density\nEND_BLOCK_DATAGRID_3D\n";
}
#
# Write header of XPLOR DCD file
#
my($savepos);
sub WriteDCDHeader {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atyi, $title, $box, $end) = @_;
    my ($a, $b, $c, $ag, $bg, $cg);
    my ($rec,$reclen);
    my ($natoms, $nsets, $delta);

    $natoms =  $#$atomx+1;
    $nsets  = 1;
    $delta = 0;
    
    $savepos = 8;
    $rec = pack "A4i9di9","CORD",$nsets,$istart,$nsavc,0,0,0,0,0,0,$deltat,
                          0,0,0,0,0,0,0,0,0;
    $reclen=pack "i", length($rec);
    print $reclen, $rec, $reclen;

    $rec = pack "iA80A80", 2, $title, "Created by CTEPROUTS/WriteDCD Keith Refson\n";
    $reclen=pack "i", length($rec);
    print $reclen, $rec, $reclen;

    $rec = pack "i", $natoms;
    $reclen=pack "i", length($rec);
    print $reclen, $rec, $reclen;
}
#
# Write the intermediate co-ordinates of a XPLOT DCD file
#
my ($dcdfirst);
sub WriteDCDTraj {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atyi, $title, $box) = @_;
    my ($a, $b, $c, $ag, $bg, $cg);
    my (@avv, @bvv, @cvv);              # Rotated unit cell vectors
    my (@cartx, @carty, @cartz);
    my @atyie;
    my $natoms;
    my $atyp;
    my @shiftlist;

#
# Do unit cell calculation
#
    ($a, $b, $c, $ag, $bg, $cg) = MATtoABC($av, $bv, $cv);

#    if (scalar (@atomxo)<= 0) {
#      @shiftlist = ExpandedCell ($atomx, $atomy, $atomz, $atyi, $box);
#    }
#    Expand($atomx, $atomy, $atomz, $atyi, \@shiftlist,
#	   \@atomxo, \@atomyo, \@atomzo, \@atyie);
    if (scalar (@atomxo) > 0) {
      TrajCon ($atomx, $atomy, $atomz, \@atomxo, \@atomyo, \@atomzo); 
    }
    @atomxo = @$atomx;
    @atomyo = @$atomy;
    @atomzo = @$atomz;
#
# Print Atom co-ords
# 
    &ABCtoMATrot($a, $b, $c, $ag, $bg, $cg, \@avv, \@bvv, \@cvv);
    FracToCart(\@avv, \@bvv, \@cvv, $atomx, $atomy, $atomz, 
                              \@cartx, \@carty, \@cartz);

    $natoms = $#cartx+1;
    $rec = pack "f$natoms", @cartx;
    $reclen = pack "i", length($rec);
    print $reclen; print $rec; print $reclen;
    $rec = pack "f$natoms", @carty;
    print $reclen; print $rec; print $reclen;
    $rec = pack "f$natoms", @cartz;
    print $reclen; print $rec; print $reclen;
}
#
# Write a Brookhaven Protein Data Bank file
#
sub WritePDB {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atyi, $title, $rotflag) = @_;
    my ($a, $b, $c, $ag, $bg, $cg);
    my (@avv, @bvv, @cvv);              # Rotated unit cell vectors
    my (@cartx, @carty, @cartz, @astar, @bstar, @cstar);
    my $iatom;
    my $atyp;

    init_atype();
#
# Do unit cell calculation
#
    ($a, $b, $c, $ag, $bg, $cg) = MATtoABC($av, $bv, $cv);
    if( $rotflag == 1 ) {
      &ABCtoMATrotaxis($a,$b,$c,$ag,$bg,$cg, \@avv, \@bvv, \@cvv);
    } elsif( $rotflag == -1 ) {
      &ABCtoMATaxis($a,$b,$c,$ag,$bg,$cg, \@avv, \@bvv, \@cvv);
    } else {
      &ABCtoMATrot($a, $b, $c, $ag, $bg, $cg, \@avv, \@bvv, \@cvv);
    }
    MATinvert(\@avv, \@bvv, \@cvv, \@astar, \@bstar, \@cstar);

    print "HEADER    UNKNOWN\n";
    $title = "" if(! defined($title) );
    print "TITLE     $title\n";
    print "AUTHOR    GENERATED BY XX2PDB (Keith Refson, 1998)\n";
    printf "%6s%9.3f%9.3f%9.3f%7.2f%7.2f%7.2f P 1\n",'CRYST1', $a, $b, $c, $ag, $bg, $cg;
    printf "SCALE%d     %9.6f %9.6f %9.6f        0.00000\n", 1, @astar;
    printf "SCALE%d     %9.6f %9.6f %9.6f        0.00000\n", 2, @bstar;
    printf "SCALE%d     %9.6f %9.6f %9.6f        0.00000\n", 3, @cstar;
#
# Print Atom co-ords
# 
    FracToCart(\@avv, \@bvv, \@cvv, $atomx, $atomy, $atomz, 
                              \@cartx, \@carty, \@cartz);
    for $iatom (0..scalar(@cartx)-1) {
        printf "%-6s%5d %2s%-.2d NON A   1    %8.3f%8.3f%8.3f %5.2f %5.2f          %2s\n", 
	'HETATM', $iatom+1,$ATYPE[$$atyi[$iatom]], 0, 
	$cartx[$iatom], $carty[$iatom], $cartz[$iatom], 1.0,0.0,$ATYPE[$$atyi[$iatom]] ;
    }
    printf "TER   %5d      NON A   1\n",scalar(@cartx);
    print "END\n";
}
#
# Write a "<seedname>.cell" for new CASTEP
#
sub WriteNewtepCell {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype, $title, $kptx, $kpty, $kptz, $wt ) = @_;
    my ($aty, $i, $fmt3, $fmt4, $fmt4b, $fmti, $fmt3b, $fmt3c, 
	$elem, $atyp, $nions);
    my @atlist1;
    my %atno;

    #
    # Create hash to look up atomic numbers from symbols
    #
    @atno{@atsym} = 0..scalar(@atsym)-1;

    #
    # See if the reader stored any ionic species information. If not
    # check the environment variable or use a default.
    #
    init_atype();

    print "#\n# $title\n#\n";
    $fmt3="%20.16f %20.16f %20.16f\n";
    $fmt4="%-8s %20.16f %20.16f %20.16f\n";
    $fmt4s="%-8s %20.16f %20.16f %20.16f SPIN=%6.3f\n";
    $fmt4b="%20.16f %20.16f %20.16f %20.16f\n";
    $fmti ="%4d%4d%4d\n";
    print "%BLOCK lattice_cart\n";
    printf $fmt3, $$av[0], $$av[1], $$av[2];
    printf $fmt3, $$bv[0], $$bv[1], $$bv[2];
    printf $fmt3, $$cv[0], $$cv[1], $$cv[2];
    print "%ENDBLOCK lattice_cart\n";

    if( $have_cell_constraints ) {
##      my ($a, $b, $c, $alpha, $beta, $gamma) =  MATtoABC($av, $bv, $cv);
##      &CheckCellConstraints($a, $b, $c, $alpha, $beta, $gamma, \@cell_constraints);
      print "\n%BLOCK cell_constraints\n";
      printf $fmti, $cell_constraints[0],$cell_constraints[1],$cell_constraints[2];
      printf $fmti, $cell_constraints[3],$cell_constraints[4],$cell_constraints[5];
      print "%ENDBLOCK cell_constraints\n";
    }

    #
    #  Construct index list sorted by atom type.
    #  N.B.  We also use the index as a secondary sort key as some
    #  sort implementations don't preserve order of equals, and 
    #  the permutation of atoms which results is undesirable.
    #
    @atlist1 = sort {$$atype[$a] <=> $$atype[$b] or $a <=> $b} 0..scalar(@$atype)-1;
    #
    # PSP files
    #
    print "\n%BLOCK species_pot\n";
    foreach $elem (keys %pspfiles) {
      printf "%-8s %s\n", $elem,$pspfiles{$elem};
    }
    print "%ENDBLOCK species_pot\n";
    #
    # Loop over atom types printing all atoms of that type.
    #
    print "\n%BLOCK positions_frac\n";
    $aty = 0;
    $nlist = scalar(@atlist1);
    while(scalar(@atlist1) > 0 && $aty <= $nlist) {
	# Get chemical symbol
        $atyp = $ATYPE[$aty];
        substr ($atyp, 2, 1) =~ tr/[A-Z]/[a-z]/ if length($atyp) > 1;
	# Strip any trailing digits
	$atyp =~ s/\d+\s*$//;
	#
	# Count ions of this species
        #
        $nions = scalar(grep $$atype[$_] == $aty, @atlist1);
        while ( scalar(@atlist1) > 0 && $$atype[$atlist1[0]] == $aty ) {
            $i = shift @atlist1;
	    if( fabs($SPIN[$i]) > 1.0e-8 ) {
	      printf $fmt4s,$atyp,round6($$atomx[$i]), round6($$atomy[$i]), round6($$atomz[$i]),$SPIN[$i];
	    } else {
	      printf $fmt4,$atyp,round6($$atomx[$i]), round6($$atomy[$i]), round6($$atomz[$i]);
	    }
        }
        $aty++;
    }
    print "%ENDBLOCK positions_frac\n";
    print "\n%BLOCK kpoints_list\n";
    for $i (0..scalar(@$kptx)-1) {
        printf $fmt4b, round6($$kptx[$i]), round6($$kpty[$i]), round6($$kptz[$i]),round6($$wt[$i]);
    }
    print "%ENDBLOCK kpoints_list\n";

    if( $have_external_stress ) {
      $fmt3a="%16.10f%16.10f%16.10f\n";
      $fmt3b="                %16.10f%16.10f\n";
      $fmt3c="                                %16.10f\n";
      print "\n%BLOCK external_pressure\n";
      print  $external_stress_unit,"\n";
      printf $fmt3a, $external_stress[0],$external_stress[1],$external_stress[2];
      printf $fmt3b, $external_stress[3],$external_stress[4];
      printf $fmt3c, $external_stress[5];
      print "%ENDBLOCK external_pressure\n";
    }

    if( $newtep_symmetry == 1 ) {
      print "\nsymmetry_generate\n";
    } elsif( $newtep_symmetry > 1 ) {
      print "%BLOCK symmetry_ops\n";
      for $nsym (0..$newtep_symmetry-1 ) {
	for $i (0..2) {
	  printf $fmt3, $sym_ops[$nsym][$i][0],$sym_ops[$nsym][$i][1],$sym_ops[$nsym][$i][2];
	}
	printf $fmt3, $sym_disps[$nsym][0],$sym_disps[$nsym][1],$sym_disps[$nsym][2];
	print "\n";
      }
      print "%ENDBLOCK symmetry_ops\n";
    }
    if ( $fix_all_cell && !$have_cell_constraints ) {
      print "fix_all_cell : T\n";
    }
    
}

sub nextline {
  s/[#!].*$//;
  while (<>)  {
    s/\r$//;
    s/[#!].*$//;
    last unless /^\s*$/;
  }
  $_;
}
#
# Write an input file for Warren and Whorlton's ACMM program
# Comp. Phys. Commun. 8(1974) 71-84
#   This computes dynamical matrix group-theory symmetry analysys
#
sub WriteACMM {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype, $kptx, $kpty, $kptz, $wt ) = @_;
    my ($aty, $i, $iatom, $ikpt, $fmt3, $fmt4, $fmt4b, $atyp, $nions);
    my (@cartx, @carty, @cartz);
    my @atlist1;

    print "ACMM input file written by Cteprouts::WriteACMM\n";
    printf "%5d%5d%5d%5d%5d\n",$#$atomx+1,0,0,0,0;
    printf "%8.5f%8.5f%8.5f%8.5f%8.5f%8.5f%8.5f%8.5f%8.5f\n",$$av[0], $$av[1], $$av[2],
      $$bv[0], $$bv[1], $$bv[2],$$cv[0], $$cv[1], $$cv[2];
    FracToCart($av, $bv, $cv, $atomx, $atomy, $atomz, 
                              \@cartx, \@carty, \@cartz);
    for $iatom (0 .. $#$atomx) {
      printf "%5d%10.5f%10.5f%10.5f\n",$$atype[$iatom]+1,$cartx[$iatom],$carty[$iatom],$cartz[$iatom];
    }
#    print "6.2831853 6.2831853 6.2831853\n";
    printf "%10.8f%10.8f%10.9f\n", 2.0*pi/$$av[0],2.0*pi/$$bv[1],2.0*pi/$$cv[2];
    FracToCartRecip($av, $bv, $cv, $kptx, $kpty, $kptz, 
                              \@cartx, \@carty, \@cartz);
    for $ikpt (0 .. $#$kptx) {
      printf "%5d%5d\n\n", 3,0;
      printf "%10.5f%10.5f%10.5f\n", $$av[0]*$cartx[$ikpt],$$bv[1]*$carty[$ikpt],$$cv[2]*$cartz[$ikpt];
    }
    
    print "\n";

}

#
# Write an input file for Bogdan Yanchintsky's "sgroup" program.
# Comp. Phys. Commun. 139(2001) 235-242
#   This computes the space group from a crystal structure
#
sub WriteSgroup {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype ) = @_;
    my ($a, $b, $c, $ag, $bg, $cg, $iatom);
    my @atlist1;

    init_atype();

    print "/SGROUP input file written by Cteprouts::WriteSgroup\n";
    print "P\n";
    ($a, $b, $c, $ag, $bg, $cg) = &MATtoABC($av, $bv, $cv);
    print $a, ' ', $b, ' ', $c, ' ', $ag, ' ', $bg, ' ', $cg, "\n";

    printf "%5d\n",$#$atomx+1;
    for $iatom (0 .. $#$atomx) {
      printf "%14.8f%14.8f%14.8f\n",$$atomx[$iatom],$$atomy[$iatom],$$atomz[$iatom];
      print $ATYPE[$$atype[$iatom]],"\n";
    }

}

#
# Write an input file for KPTGEN
#
#
# We could adapt this to accept an input set of kpoints and 
# write the necessaries to analyse it.
#
sub WriteKptGen {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype, $title ) = @_;
    my (@avsc,@bvsc,@cvsc,$ascale,$bscale,$cscale, $i,$aty);
    my @atlist1;

    $title = "XXX2kptgen - Keith Refson" if $title eq "";

    print $title,"\n";

    # Compute and print scale factors
    $ascale = sqrt($$av[0]*$$av[0]+$$av[1]*$$av[1]+$$av[2]*$$av[2]);
    $bscale = sqrt($$bv[0]*$$bv[0]+$$bv[1]*$$bv[1]+$$bv[2]*$$bv[2]);
    $cscale = sqrt($$cv[0]*$$cv[0]+$$cv[1]*$$cv[1]+$$cv[2]*$$cv[2]);

    printf "%18.12f %18.12f %18.12f\n", $ascale,$bscale,$cscale;
    # Compute and print scaled cell vectors
    for $i (0..2) {
      $avsc[$i] = $$av[$i]/$ascale;
      $bvsc[$i] = $$bv[$i]/$bscale;
      $cvsc[$i] = $$cv[$i]/$cscale;
    }
    printf "%18.12f %18.12f %18.12f %18.12f %18.12f %18.12f %18.12f %18.12f %18.12f \n",
      $avsc[0],$avsc[1],$avsc[2], $bvsc[0],$bvsc[1],$bvsc[2], $cvsc[0],$cvsc[1],$cvsc[2];
    # Atom number and number of species
    print scalar(@$atomx),"   ",scalar(@ATYPE),"\n";
    foreach $aty (sort {$a <=> $b} @$atype) {
      printf "%3d ",$aty+1;
    }
    print "\n";
    # Now the atoms
    for $i (sort {$$atype[$a] <=> $$atype[$b]} 0..$#$atomx) {
      printf "%18.12f %18.12f %18.12f\n",round6($$atomx[$i]),round6($$atomy[$i]),round6($$atomz[$i]);
    }
    # Ibrav=0 since we are generating
    print "0  0\n";
    print "0\n";
    printf "2 2 2 0 0 0\n"
}

#
# "Static" storage of atom co-ordinates
#
my (@atomxoWEP, @atomyoWEP, @atomzoWEP, @shiftlist);
sub WriteExpandedPDB {
    #
    # Expands co-ordinate list by pbc replication and writes a PDB file.
    # If called repeatedly it joins up trajectories fragmented by
    # periodic boundaries on the assumption that this is part of an 
    # animation sequence. 
    #
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atyi, $title, $box) = @_;
    my (@atomxe, @atomye, @atomze, @atyie);

    if (scalar (@atomxoWEP)<= 0) {
        @shiftlist = ExpandedCell ($atomx, $atomy, $atomz, $atyi, $box);
    } else {
        TrajCon ($atomx, $atomy, $atomz, \@atomxoWEP, \@atomyoWEP, \@atomzoWEP);
    }

    Expand($atomx, $atomy, $atomz, $atyi, \@shiftlist,
           \@atomxe, \@atomye, \@atomze, \@atyie);
    local $, = " ";
#    print STDERR @$av,@$bv,@$cv,"\n";
    printf  STDERR "Entered WriteExpandedPDB with %d atoms expanded to %d\n",$#{$atomx}+1, $#atomxe+1 if $debug;

    printf  STDERR "Calling WritePDB with %d atoms\n",$#atomxe+1 if $debug;
    WritePDB($av, $bv, $cv, \@atomxe, \@atomye, \@atomze, \@atyie);
    @atomxoWEP = @$atomx;
    @atomyoWEP = @$atomy;
    @atomzoWEP = @$atomz;
}

########################################################################
#
# B E G I N I N G  O F   R E A D  R O U T I N E S
#
########################################################################
#
# ReadViewmol.  Read one of viewmol's output files
#
sub ReadViewmol {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype) = @_;
    my (@atomxc, @atomyc, @atomzc);
    my (@Fld, $atyp);
    my ($a, $b, $c, $alpha, $beta, $gamma) = (1.0,1.0,1.0,$pi/2,$pi/2,$pi/2);
    
    while (<>) {
	last if (/^\$end/);

	($a, $b, $c, $alpha, $beta, $gamma) = 
	  ($abohr*$1, $abohr*$2, $abohr*$3, $4, $5, $6)
	   if( /^\$unitcell(\s+$number){6}/);
	
	if (/^\$coord/ ) {
	    $_ = <>;
	    while (!/^\$/) {
		@Fld = split;
		$atyp = $Fld[3];

		push @$atype, atom_type($atyp);
		push @atomxc, $abohr*$Fld[0];
		push @atomyc, $abohr*$Fld[1];
		push @atomzc, $abohr*$Fld[2];
	        $_ = <>;
	    }
	}
    }
    #
    # Convert Cartesian co-ordinates to fractional.
    #
    &ABCtoMAT($a, $b, $c, $alpha, $beta, $gamma, $av, $bv, $cv);

    &CheckCellParameters( $av, $bv, $cv );
    &CartToFrac($av,$bv,$cv, \@atomxc, \@atomyc, \@atomzc, 
		                  $atomx, $atomy, $atomz);

}
#
# Read co-ordinates from Brookhaven Protein Data Bank format file
#
sub ReadPDB {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype, $title, $rotated) = @_;
    my ($a, $b, $c, $aa, $ba, $ca);
    my ($n, $vol, $atyp, $atx, $aty, $atz, $junk, $atymax, $natom);
    my ($ap, $bp, $cp, $aap, $bap, $cap);
    my (@cartx, @carty, @cartz);
    my (@astar, @bstar, @cstar);

    while (<>) {
        if ( /^TITLE/ ) {
	  ($junk, $$title) = unpack "a10 a62", $_;
	  chomp $$title;
	}
        if ( /^CRYST1/i ) {
            ($junk, $a, $b, $c, $aa, $ba, $ca) = split;
	    if( $rotated ) {
	      &ABCtoMATrot($a,$b,$c,$aa,$ba,$ca, $av, $bv, $cv);
	    } else {
	      &ABCtoMAT($a,$b,$c,$aa,$ba,$ca, $av, $bv, $cv);
	    }
        }
	if ( /^SCALE1/ ) {
	    ($junk, $n, $junk, @astar) = unpack "A5 A1 A4 A10 A10 A10",$_;
	}
	if ( /^SCALE2/ ) {
	    ($junk, $n, $junk, @bstar) = unpack "A5 A1 A4 A10 A10 A10",$_;
	}
	if ( /^SCALE3/ ) {
	    ($junk, $n, $junk, @cstar) = unpack "A5 A1 A4 A10 A10 A10",$_;
	    MATinvert(\@astar, \@bstar, \@cstar, $av, $bv, $cv);
	    ($ap, $bp, $cp, $aap, $bap, $cap) = MATtoABC($av, $bv, $cv);
#	    printf STDERR "%9.3f%9.3f%9.3f%7.2f%7.2f%7.2f P 1\n",
#	      $ap, $bp, $cp, $aap, $bap, $cap;
	}
        if ( /^ATOM/i ||/^HETATM/i ) { 
            ($junk, $atyp, $junk, $junk, $atx, $aty, $atz, $junk) = 
                unpack "A12 A2 A2 A14 A8 A8 A8 A14",$_;

            $atyp =~ s/\s+//g;
            push @$atype, atom_type($atyp);
            push @cartx, $atx;
            push @carty, $aty;
            push @cartz, $atz;
            $natom++;
        }
        if ( /^END/i ) {last; }
    }

    &CheckCellParameters( $av, $bv, $cv );
    &CartToFrac($av, $bv, $cv, \@cartx, \@carty, \@cartz, 
		                  $atomx, $atomy, $atomz);
    
}
#
# Read co-ordinates from Cambridge CSSR format file
#
sub ReadCSSR {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype, $spgr, $title) = @_;
    my ($a, $b, $c, $aa, $ba, $ca);
    my ($vol, $atyp, $atx, $aty, $atz, $junk, $atymax, $orthflag);
    my ($iat, $natom, $serno);
    my (@cartx, @carty, @cartz);

    ($junk, $a, $b, $c) = unpack "a38 a8 a8 a8", <>;
    ($junk, $aa, $ba, $ca, $junk, $junk, $$spgr) = unpack "a21 a8 a8 a8 a4 a10 a11", <>;

    &ABCtoMATrot($a,$b,$c,$aa,$ba,$ca, $av, $bv, $cv);

    ($natom, $orthflag, $$title) = unpack "a4 a4 x a60", <>;
    $$title = "ReadCSSR - Keith Refson" if $title == "";

    if( $a > 0 && $b > 0 && $c > 0 && $aa > 0 && $ba > 0 && $ca > 0 ) {
      &ABCtoMATrot($a,$b,$c,$aa,$ba,$ca, $av, $bv, $cv);
    } elsif ($orthflag  == 0) {
      die "ReadCSSR:No unit cell parameters supplied but orthflag = 0";
    } else {
      @$av = (1, 0, 0);
      @$bv = (0, 1, 0);
      @$cv = (0, 0, 1);
    }

    $junk = <>;


    for($iat = 0; $iat < $natom; $iat++) {
      ($serno, $atyp, $atx, $aty, $atz, $junk) = unpack "a4 x a4 x2 a9 x a9 x a9", <>;

      $atyp =~ s/\s+//g;
      $atyp =~ s/\d+//;

      push @$atype, atom_type($atyp);
      if ( $orthflag > 0) {
	push @cartx, $atx;
	push @carty, $aty;
	push @cartz, $atz;
      } else {
	push @$atomx, $atx;
	push @$atomy, $aty;
	push @$atomz, $atz;
      }
    }

    &CheckCellParameters( $av, $bv, $cv );
    if ( $orthflag > 0) {
      &CartToFrac($av, $bv, $cv, \@cartx, \@carty, \@cartz, 
		  $atomx, $atomy, $atomz);
    }
    
}
#
# Read co-ordinates from Shelx format file
#
sub ReadShelXL {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype, $spgr, $title) = @_;
    my ($a, $b, $c, $aa, $ba, $ca);
    my ($ndims, $iat, $atyp, $atx, $aty, $atz, $junk);

    while (<>) {
      chop;
      if ( /^TITL/i ) {
	($junk,$$title) = split;
      }
      if ( /^CELL/i ) {
	($junk, $junk, $a, $b, $c, $aa, $ba, $ca) = split;
	&ABCtoMAT($a,$b,$c,$aa,$ba,$ca, $av, $bv, $cv);
      }
      if ( /^\s*LATT/i ) {
	# Lattice type
	
      }
      if ( /^\s*SYMM/i ) {
	# Symmetry operations
	die "Implementation restriction - SYMM cards not supported\n";
      }
      if ( /^\s*SFAC/i ) {
	# Atom types
	@ATYPE=split;
	shift @ATYPE;
#	print STDERR "$ATYPE[0]  $ATYPE[1]  $ATYPE[2]\n";
      }
      if ( /^\s*\w+\s+(\d+)\s+($fnumber)\s+($fnumber)\s+($fnumber)\s+$fnumber/i ) {
	push @$atype, $1-1;
	push @$atomx, $2;
	push @$atomy, $3;
	push @$atomz, $4;
      }
      last if ( /^\s*END/i ) or eof;
    }

  &CheckCellParameters( $av, $bv, $cv );
}
#
# Read co-ordinates from Insight XTL format file
#
sub ReadXTL {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype, $spgr, $title) = @_;
    my ($a, $b, $c, $aa, $ba, $ca);
    my ($ndims, $iat, $atyp, $atx, $aty, $atz, $junk, $natom);

    $iat = 0;
    $ndims = 3;
    while (<>) {
      chop;
        if ( /^TITLE/i ) {
	  ($junk,$$title) = split;
	}
	if ( /^DIMENSION/i ) {
	  ($junk, $ndims) = split;
	}
	if ( /^CELL/i ) {
	  if ( /^CELL\s+[\d]+/i ) {
	    s/^CELL\s//i;
	  } else {
	    $_ = <>;
	  }
	  if ($ndims == 2 ) {
	    ($a, $b, $ca) = split;
	    $c = 1.0;
	    $aa = $ba = 90.0;
	  } else {
	    ($a, $b, $c, $aa, $ba, $ca) = split;
	  }
	  &ABCtoMAT($a,$b,$c,$aa,$ba,$ca, $av, $bv, $cv);
	}
	if ( /^SYMMETRY/i ) {
	  # Ignore this for now.
	}
		
	if ( /^SYMM MAT/i ) {
	  # Symmetry handling can come later.
	}

	if ( /^ATOMS/i ) {
	  $_ = <>;
	  while( <> ) {
	    last if ( /^EOF/i );
	    ($atyp, $atx, $aty, $atz, $junk) = split;
	    $atyp =~ s/\s+//g;

	    push @$atype, atom_type($atyp);
	    push @$atomx, $atx;
	    push @$atomy, $aty;
	    push @$atomz, $atz;
	    $iat++;
	  }
	}
        last if ( /^EOF/i ) or eof;
      }

    &CheckCellParameters( $av, $bv, $cv );
  }

#
# Read VASP OUTCAR main output file
# Extract *last* set of atomic co-ords and k-point set.
# The strategy here is to ready any likely set of co-ordinates
# and accept all of the forms they may be in.
#
sub ReadVASP {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype, $kptx, $kpty, $kptz, $wt ) = @_;
    my ($row, $iatom, $kpline, $nkpts, $junk, $aty_found, $atyp, $i, $title, $crds);
    my ($atomno, $kpflag, $atyn);
    my (@Fld, @natoms, @cartx, @carty, @cartz);
    my (@my_atype);

    #$debug = 1;
    $aty_found = 0;

    if (open COORDS,"<POSCAR" ) {
      $title = <COORDS>;
      $crds  = <COORDS>;
      for $i (0..2) {
        $crds  = <COORDS>;
        @Fld = split /[\s]+/, $crds;
        push @$av, $Fld[1];
        push @$bv, $Fld[2];
        push @$cv, $Fld[3];
      }
      $crds  = <COORDS>;
      @natoms =  split /[\s]+/, $crds;
      shift @natoms;
    }


    while (<>) {
        chop;   # strip record separator
        @Fld = split /[\s]+/;
	#
	# Numbers of ion species and ions
	if(/^\s*ions per type =/) {
	  s/^\s*ions per type =//;
	  @natoms =  split /[\s]+/, $_;
	  shift @natoms;
	}
	#
	# Identify ion species
	#
	#if ( /^   VRHFIN =([A-Za-z][A-Za-z]?):/ ) {
	#  push @ATYPE, $1;
	#}
	if(/^\s*POTCAR:/) {
	  ($junk,$junk,$atyn,$junk) = split;
	  $atyn =~ s/_.*//;
	  $styn = substr $atyn,0,2;
	  $my_atype[$atype_found] = $styn;
	  $atype_found++;
	}

        if (/direct Lattice.*reciprocal lattice/i ... /^\s*$/) {
            if (/direct Lattice/i) {
                @$av = ();
                @$bv = ();
                @$cv = ();
            }
            if (/^(\s+$fnumber){3,6}\s*\r?$/) {
                push @$av, $Fld[1];
                push @$bv, $Fld[2];
                push @$cv, $Fld[3];
            }
        }

        #
        if (/^\s+POSITION  *TOTAL-FORCE \(eV\/Angst\)\r?$/ ... /^\s*$/ ) {
            if (/^\s+POSITION/) {
                @cartx = ();
                @carty = ();
                @cartz = ();
                @$atype = ();
		$atyp=0;
		$atomno=1;
            }
            if (! /-{72}/ && /^(\s*$fnumber){6}\r?$/) {
                push @cartx, $Fld[1];
                push @carty, $Fld[2];
                push @cartz, $Fld[3];
                push @$atype, atom_type($my_atype[$atyp]);
		$atomno++;
		if ($atomno > $natoms[$atyp] ) {
		  $atyp++;
		  $atomno = 1;
		}

            }
        }

        #
        #  Only record first block of special k-points.
        #
        $kpflag = 1 if ( /^ k-points in reciprocal (coordinates|lattice) and weights: / );
        if (/^\s+k-points in reciprocal (coordinates|lattice) and weights: / ... /^\s*$/) {
            if ( $kpflag ) {
                @$kptx = ();
                @$kpty = ();
                @$kptz = ();
                @$wt = ();
            }
            $kpflag = 0;
	    if(/($fnumber){4}/) {
	      push @$kptx, $Fld[1];
	      push @$kpty, $Fld[2];
	      push @$kptz, $Fld[3];
	      push @$wt,   $Fld[4];
	    }
        }

      }
    &CartToFrac($av, $bv, $cv, \@cartx, \@carty, \@cartz, 
		                  $atomx, $atomy, $atomz);

}
#
# Read Academic CASTEP or CETEP main output or fort.4 file.
# Extract *last* set of atomic co-ords and k-point set.
# The strategy here is to ready any likely set of co-ordinates
# and accept all of the forms they may be in.
#
sub ReadCetep {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype, $kptx, $kpty, $kptz, $wt ) = @_;
    my (@Fld, $row, $iatom, $kpline, $nkpts, $junk);
    my ($atp, $atx, $aty, $atz, $kpflag);

    while (<>) {
        chop;   # strip record separator
        @Fld = split /[\s]+/;

        if (/\( DIRC\(I,J\) \):/ ... !/(\s*$fnumber){3}\r?$/) {
            if (/\( DIRC\(I,J\) \)/) {
                @$av = ();
                @$bv = ();
                @$cv = ();
            }
            if (/\s$fnumber\r?$/) {
                push @$av, $Fld[1];
                push @$bv, $Fld[2];
                push @$cv, $Fld[3];
            }
        }

        #
        # N.B.  The NSP ATOM a1 a2 a3 X Y Z lines in CETEP have NSP and
        # ATOM reversed so these are handled separately.
        #
        if (/^ NSP ATOM.*Fx *Fy *Fz\r?$/ ... /$nonnumeric/ ) {
            if (/^ NSP ATOM/) {
                @$atomx = ();
                @$atomy = ();
                @$atomz = ();
                @$atype = ();
            }
            if (! /-{72}/ && /(\s*$number){8}\r?$/) {
                push @$atomx, $Fld[3];
                push @$atomy, $Fld[4];
                push @$atomz, $Fld[5];
                push @$atype, $Fld[1];
            }
        }

        if (/^ NSP ATOM.*X *Y *Z\r?$/ ... /$nonnumeric/ ) {
            if (/^ NSP ATOM/) {
                @$atomx = ();
                @$atomy = ();
                @$atomz = ();
                @$atype = ();
            }
            if (! /-{72}/ && /(\s*$number){8}\r?$/) {
                push @$atomx, $Fld[3];
                push @$atomy, $Fld[4];
                push @$atomz, $Fld[5];
                push @$atype, $Fld[2];
            }
        }

        if (/^  ION *\d\d* TYPE/) {
            if (/ION    1 TYPE 1 AT/) {
                @$atomx = ();
                @$atomy = ();
                @$atomz = ();
                @$atype = ();
            }
            if (!/NaN/) {
		($atp, $atx, $aty, $atz) = unpack "x16 a1 x5 a9 a9 a9", $_;
                push @$atomx, $atx;
                push @$atomy, $aty;
                push @$atomz, $atz;
                push @$atype, $atp;
            }
        }
        #
        #  Only record first block of special k-points.
        #
        $kpflag = 1 if ( !/^  SPECIAL K-POINT:/ );
        if (/^  SPECIAL K-POINT:/) {
            if ( $kpflag ) {
                @$kptx = ();
                @$kpty = ();
                @$kptz = ();
                @$wt = ();
            }
            $kpflag = 0;
            push @$kptx, $Fld[3];
            push @$kpty, $Fld[4];
            push @$kptz, $Fld[5];
            push @$wt,   $Fld[8];
        }

    }
    &CheckCellParameters( $av, $bv, $cv );
}
#
# Read Academic CASTEP or CETEP main output or fort.4 file.
# Extract *all* sets of atomic co-ords and call supplied
# function repeatedly to handle the extracted co-ordinates.
#
sub ReadCetepAnim {
    my ($begfunc, $filefunc, $outfunc, $endfunc, $basename, $box, $title) = @_;
    my (@forcx, @forcy, @forcz);
    my ($iatom, $icycle, $toten, $gnorm);
    my ($nat, $row, @av, @bv, @cv, @atomx, @atomy, @atomz, $filename);
    my ($atp, $atx, $aty, $atz, $kpflag);
    my (@atype, @Fld, $ifld);

    while (<>) {
        chop;   # strip record separator
        @Fld = split /[)\s]+/;

        if (/\( DIRC\(I,J\) \):/ ... !/(\*s$fnumber){3}\r?$/) {
            if (/\( DIRC\(I,J\) \)/) {
                @av = ();
                @bv = ();
                @cv = ();
            }
            if (/\s$fnumber\r?$/) {
                push @av, $Fld[1];
                push @bv, $Fld[2];
                push @cv, $Fld[3];
            }   
        }


        if (/^  ION *\d\d* TYPE/) {
            if (/ION    1 TYPE 1 AT/) {
                @atype = ();
            }
            if (!/NaN/) {
		($atp, $atx, $aty, $atz) = unpack "x16 a1 x5 a9 a9 a9", $_;
                push @atype, $atp;
            }
        }
        $toten = $1 if (/^ TOTAL FREE ENERGY IS *($number)/);
        #
        # Forces
        #
        if (/^ *FORCES EXERTED ON IONS :/) {
            $iatom = 0;
	    $gnorm = 0;
	  }
        if (/^ *Atom *Fx *Fy *Fz *Total/ ... /$nonnumeric/) {
            if (/^(\s*$number){5}\r?$/ && ! /-{60}/ ) {
	      $iatom++;
	      $ifld = 3;
	      $ifld++ unless ($Fld[$ifld] =~ /\./);
	      $forcx[$iatom] = $Fld[$ifld++];
	      $forcy[$iatom] = $Fld[$ifld++];
	      $forcz[$iatom] = $Fld[$ifld++];
	      $gnorm += $Fld[$ifld]*$Fld[$ifld];
	    }
        }
        #
        # N.B.  The NSP ATOM a1 a2 a3 X Y Z lines in CETEP have NSP and
        # ATOM reversed.  
        #
        if (/^ NSP ATOM *a1 *a2 *a3\r?$/ ... /$nonnumeric/ ) {
            if (/^ NSP ATOM/) {
                @atomx = ();
                @atomy = ();
                @atomz = ();
#                @atype = ();
            }
            if (! /-{72}/ && /^(\s*$number){6}\r?$/) {
                push @atomx, $Fld[3];
                push @atomy, $Fld[4];
                push @atomz, $Fld[5];
#                push @atype, $Fld[2];
            }
	  }

          if ( @atomx > 0 && (/-------------------- (BFGS|MD) STEP   =   / || /- Stopping\r?$/) ) { 
	    $gnorm = sqrt($gnorm);
            $,=" ";
	    $icycle++;
	    &$begfunc(\@av, \@bv, \@cv, \@atomx, \@atomy, \@atomz, \@atype, $title, $box, 1) if ($icycle == 1);
	    &$filefunc($basename, $outfunc, \@av, \@bv, \@cv, 
                       \@atomx, \@atomy, \@atomz, \@atype, $title, $box, 
                       \@forcx, \@forcy, \@forcz, $icycle, $toten, $gnorm  ); 
        }

    }
    &CheckCellParameters( $av, $bv, $cv );
    &$endfunc();
#print STDERR "\n";
}
#
# Read Matt Segall's F90 CETEP main output file.
# Extract *last* set of atomic co-ords and k-point set.
#
sub ReadNewCetep {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype, $kptx, $kpty, $kptz, $wt ) = @_;
    
    my (@Fld);
    my ($asym, $atyp, $atymax, $nkpts, $junk, $endatoms);

    while (<>) {
        chop;   # strip record separator
        @Fld = split;

        if (/^  The basis-set used when placing atoms/) {
            @$av = ();
            @$bv = ();
            @$cv = ();
            $junk = <>;
            foreach (0..2){
                $_ = <>;
                @Fld = split ;
                push @$av, $Fld[0];
                push @$bv, $Fld[1];
                push @$cv, $Fld[2];
            }   
        }

        #
        # Extract atomic co-ordinate data.
        #
        if (/^ Spec\. Atom.*fx *fy *fz\r?$/ ... $endatoms ==2 ) {
            if (/^ Spec\. Atom/) {
                $endatoms = 0;
                @$atomx = ();
                @$atomy = ();
                @$atomz = ();
                @$atype = ();
                $atymax = 0;
                $asym = "";
                next;
            }
            $endatoms++ if /^ -+\r?$/;
            if (scalar(@Fld) == 8) {
                push @$atomx, $Fld[2];
                push @$atomy, $Fld[3];
                push @$atomz, $Fld[4];
                $atyp = $Fld[0];
                push @$atype, atom_type($atyp);
            }
        }

        #
        #  Get special K-point
        #
        if ( /^ Special K-points:/ ){
            @$kptx = ();
            @$kpty = ();
            @$kptz = ();
            @$wt = ();
            $junk = <>;
            $_ = <>;
            while (/Weight=/) {
                @Fld = split;
                push @$kptx, $Fld[0];
                push @$kpty, $Fld[1];
                push @$kptz, $Fld[2];
                push @$wt,   $Fld[4];
                $_ = <>;
            }
        }
    }

    &CheckCellParameters( $av, $bv, $cv );
}
#
#  Read CASTEP or CETEP fort.15 or Cerius 2  CASTEP .geom files.
#
sub ReadFort15 {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype, $kptx, $kpty, $kptz, $wt ) = @_;
    my ($natom, $natomsp, $atom1sp, $nsp, $i, $junk, @Fld, $nkpts, @rmove);

    #
    # First 3 lines contain unit cell vectors. Skip 3-6
    #
    foreach $i ( (0,1,2) ) {
        ($$av[$i], $$bv[$i], $$cv[$i]) = split ' ', scalar(<>);
    }
    foreach $i ( (0,1,2) ) {
        $junk = <>;
    }
    #
    # Main loop over ionic species.
    #
    $natom = 0;
    @Fld = split ' ', scalar(<>);
    SPECIES: while ($#Fld == 4) {
        $natomsp = 0;
        $atom1sp = $natom;
        #
        # Loop over ions in this species.  End of species is detected
        # if either (a) there are < 4 numbers on line or
        # (b) the co-ordinates are identical to the first of the species.
        # (Cannot count on (a))
        while ($#Fld == 4 
               && (   $Fld[0] ne $$atomx[$atom1sp] 
                   || $Fld[1] ne $$atomy[$atom1sp] 
                   || $Fld[2] ne $$atomz[$atom1sp] )) {
            #
            # This is a new ion (or possibly CETEP K-pt. Add it.
            #
            $natomsp++;
            $natom++;
            push @$atype, $nsp;
            push @$atomx, $Fld[0];
            push @$atomy, $Fld[1];
            push @$atomz, $Fld[2];
            push @rmove, $Fld[3];
            @Fld = split ' ', scalar(<>);
            last SPECIES if eof;
        }
	last SPECIES if eof || @Fld < 3;
        #
        # Skip second set of co-ords
        #
        for (0..$natomsp-1) { 
            #
            #  This is POSIOL - skip NIONS records (including this one)
            #  Also marks end of prev. species
            #
            @Fld = split ' ', scalar(<>);
	    last SPECIES if eof || @Fld < 3;
	    $natomsp--;
        }
        $nsp++;
    }
    
    #
    # If natomsp > 0 we have misread CETEP k-points as ions 
    #
    # print STDERR  "NATOMSP=",$natomsp,"\n";
    if($natomsp > 0) {
        $nkpts = $natomsp;
        $natom -= $nkpts;
        $natomsp = 0;
        $nsp--;
        # 
        # Move entries from atoms positions list to k-point list
        #
        for(0..$nkpts-1) {
            pop @$atype;
            unshift @$kptx, pop(@$atomx);
            unshift @$kpty, pop(@$atomy);
            unshift @$kptz, pop(@$atomz);
            unshift @$wt,   pop(@rmove);
        }
    } elsif ($#Fld == 3) {
        #
        # This looks like CASTEP fort.15 k-points
        #
        while ($#Fld == 3) {
            $nkpts++;
            push @$kptx, $Fld[0];
            push @$kpty, $Fld[1];
            push @$kptz, $Fld[2];
            @Fld = split ' ', scalar(<>);
        }
        
        for( 0..$nkpts-1 ) {
            push @$wt,   $Fld[0];
            @Fld = split ' ', scalar(<>);
        }
    }
    #
    # Read any remaining lines in file
    #
    $junk = <> while(!eof);

    &CheckCellParameters( $av, $bv, $cv );
}
#
# Read RUN290 fort.3 or Cerius2 .symm file
#
sub ReadSymm {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype, $kptx, $kpty, $kptz, $wt ) = @_;

    my ($junk, $natom, $atyp, $atx, $aty, $atz, $nlines);
    my ($nx, $ny, $nz, $nkpts, $offset, $wtkpt, $kx, $ky, $kz, $totwt);

    $totwt = 0;

    $junk = <>; # Version, date etc
    $junk = <>; # A comment
    $junk = <>; # IFIRST
    $natom = <>;  # Number of atoms
    chop $natom;
    @$av = split ' ', scalar(<>);
    @$bv = split ' ', scalar(<>);
    @$cv = split ' ', scalar(<>);
    my @B1  = split ' ', scalar(<>);
    my @B2  = split ' ', scalar(<>);
    my @B3  = split ' ', scalar(<>);

    @$atype = ();
    @$atomx = ();@$atomy = ();@$atomz = ();
    foreach (0 .. $natom-1) {
        ($atyp, $atx, $aty, $atz) = split ' ', scalar(<>);
        push @$atype, $atyp;
        push @$atomx, $B1[0]*$atx + $B1[1]*$aty + $B1[2]*$atz;
        push @$atomy, $B2[0]*$atx + $B2[1]*$aty + $B2[2]*$atz;
        push @$atomz, $B3[0]*$atx + $B3[1]*$aty + $B3[2]*$atz;
    }

    $nlines = 1+4+48+int((48*$natom+8)/9)+3*49+1; # print $nlines,"\n";

    foreach (0..$nlines-1) {
        $junk = <>;
    }

    $nkpts = <>; # Number of k-points
    chop $nkpts;
    ($nx, $ny, $nz, $offset) = split ' ', scalar(<>);

    @$wt = ();
    @$kptx = (); @$kpty = (); @$kptz= (); 
    foreach (0..$nkpts-1) {
        ($wtkpt, $kx, $ky, $kz) = split ' ', scalar(<>);
        push @$wt, $wtkpt;
        push @$kptx, $$av[0]*$kx + $$av[1]*$ky + $$av[2]*$kz;
        push @$kpty, $$bv[0]*$kx + $$bv[1]*$ky + $$bv[2]*$kz;
        push @$kptz, $$cv[0]*$kx + $$cv[1]*$ky + $$cv[2]*$kz;
        $totwt = $totwt+$wtkpt;
    }

    foreach $wtkpt (@$wt) {
        $wtkpt /= $totwt;
    }

    &CheckCellParameters( $av, $bv, $cv );
}

#
# Read Cerius 2 CASTEP .cst files
# Extract *last* set of atomic co-ords and k-point set.
#
sub ReadCerius {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype, $kptx, $kpty, $kptz, $wt ) = @_;
    my ($a, $b, $c, $aa, $ba, $ca);
    my (@Fld, $iatom, $coordflg, $nkpts, $junk, $kpflg);
    my ($caa, $cba, $cca);

    $coordflg = 0;

    while (<>) {
        chop;   # strip record separator
        @Fld = split ;

        $a = $1 , $aa = $2 if( /^ +a =  *($number) +(?:Free|Fixed)? +alpha = +($number)/);
        $b = $1 , $ba = $2 if( /^ +b =  *($number) +(?:Free|Fixed)? +beta  = +($number)/);
        $c = $1 , $ca = $2 if( /^ +c =  *($number) +(?:Free|Fixed)? +gamma = +($number)/);

        if (/Element  Atom     Fractional coordinates/) {
            $iatom = 0;
            $coordflg = 1;
        }
        if ($coordflg > 0 && (/-{72}/ ... /-{72}/)) {
            if (! /-{72}/ ) {
                $$atomx[$iatom] = $Fld[2];
                $$atomy[$iatom] = $Fld[3];
                $$atomz[$iatom] = $Fld[4];
                $$atype[$iatom] = atom_type($Fld[0]);
                $iatom++;
            } else {
                $coordflg++;
            }
            $coordflg = 0 if ($coordflg ==3);
        }
        #
        #  Only record first block of special k-points.
        #
        if (/ Special k-points for Brillouin zone sampling/ .. /^\r?$/ ) {
            if (/^(\s*$number)+\r?$/ && /\d/ && ! $kpflg) {
                ($junk, $junk, $$kptx[$nkpts], $$kpty[$nkpts], $$kptz[$nkpts], $$wt[$nkpts], $junk) = split;
                $nkpts++;
            }
            if (/^ \+(\s*$number)+\s*\+\r?$/ && /\d/ && ! $kpflg) {
                ($junk, $junk, $$kptx[$nkpts], $$kpty[$nkpts], $$kptz[$nkpts], $$wt[$nkpts], $junk) = split;
                $nkpts++;
            }
            $kpflg++ if /^\r?$/;
        }
    }

    &ABCtoMAT($a, $b, $c, $aa, $ba, $ca, $av, $bv, $cv);

    &CheckCellParameters( $av, $bv, $cv );
}

#
# Read MSI CASTEP main out .cst file.
# Extract *all* sets of atomic co-ords and call supplied
# function repeatedly to handle the extracted co-ordinates.
#
sub ReadCeriusAnim {
    my ($begfunc, $filefunc, $outfunc, $endfunc, $basename, $box) = @_;
    my ($nat, $row, @av, @bv, @cv, @atomx, @atomy, @atomz, @atype);
    my ($filename);
    my (@forcx, @forcy, @forcz, $icycle, $toten, $gnorm);
    my ($junk, $junk1, $junk2, $stress, $estress);
    my (@atomxn, @atomyn, @atomzn);
    my (@atomxc, @atomyc, @atomzc);
    my (@eigen, @occ);
    my @Fld;
    my ($coordname, $cellname,$forcename, $title );
    my ($a, $b, $c, $aa, $ba, $ca);
    my ($gradflg, $gradflg0, $coordflg, $outflag) = (0,0, 0);
    my ($coordfileflag, $cellfileflag,$forcefileflag);
    my ($atyp,$asym,$iat,$natoms,$nbk,$nkpts,);
    
    $, = " ";

    $coordname = $basename;
    $coordname =~ s/\.cst/.coord/;
    if (open COORDS,"<$coordname" ) {
      $title = <COORDS>;
      $coordfileflag++;
    }
    $cellname = $basename;
    $cellname =~ s/\.cst/.cell/;
    if (open CELL,"<$cellname" ) {
      $title = <CELL>;
      $cellfileflag++;
    }
    $forcename = $basename;
    $forcename =~ s/\.cst/.force/;
    if (open FORCES,"<$forcename" ) {
      $title = <FORCES>;
      $forcefileflag++;
    }

    while (<>) {
        chop;   # strip record separator
        @Fld = split /[)\s]+/;
        #
        #  Title, energy, RMS force and end-of-cycle locators.
        #
        if (/^ \** Title \**/) {
	  $title = <>;
	  chop $title;
        }
       
        $gnorm = $1 if (/^> RMS  Force  *($number)/);
        $toten = $1  if (/^ TOTAL ENERGY IS *($number)/);
        #
        # Are we ready to write gradient info?  Answer depends
        # on whether we are reading coords from .cst or .coord file.
        #
        if ($coordfileflag ) {
            $gradflg = 1 if (/^> Energy change per atom/||
                             /^>>>>> Final electronic minimization /||
			     /^> +Time +Internal/);
        } 
        $outflag++ if (/Single point energy calculation converged/ );
        $outflag++ if (/^ +\* RMS convergence of band energies/ );
        #
        # Unit Cell
        #
        $a = $1 , $aa = $2 if( /^ +a =  *($number) +(?:Free|Fixed)? +alpha = +($number)/);
        $b = $1 , $ba = $2 if( /^ +b =  *($number) +(?:Free|Fixed)? +beta  = +($number)/);
        $c = $1 , $ca = $2 if( /^ +c =  *($number) +(?:Free|Fixed)? +gamma = +($number)/);

	&ABCtoMAT($a, $b, $c, $aa, $ba, $ca, \@av, \@bv, \@cv) if (/^ +Cell volume/);

        #
        # Initial fractional co-ordinates
        #
        if (/^ x  Element    Atom     Fractional coordinates of atoms / ) {
	  @atomx = ();
	  @atomy = ();
	  @atomz = ();
	}
        if (/^ x  Element +Atom +Fractional coordinates of atoms / .. /^ x+\r?$/) {
	  if (/^ x +([A-Za-z]{1,2}) +\d+(\s+$number){3}/){
	    push @atype, atom_type($1);
	    push @atomx, $2;
	    push @atomy, $3;
	    push @atomz, $4;
	  }
        }

        #
        # Fractional Co-ordinates after geometry optimization/MD
        #
        if (/^ Element  Atom     Fractional coordinates  /) {
	  @atomxn = ();
	  @atomyn = ();
	  @atomzn = ();
	  @forcx = ();
	  @forcy = ();
	  @forcz = ();
	  $coordflg = 1;
        }
        if ($coordflg > 0 && (/-{72}/ ... /-{72}/)) {
            if (! /-{72}/ ) {
                push @atomxn, $Fld[3];
                push @atomyn, $Fld[4];
                push @atomzn, $Fld[5];
                push @forcx, $Fld[6];
                push @forcy, $Fld[7];
                push @forcz, $Fld[8];
            } else {
                $coordflg++;
            }
	    if( $coordflg == 3) {
		$coordflg = 0;
	        $gradflg = 1 if ( $gradflg0 && $coordfileflag == 0);
		$gradflg0 = 1 if ($coordfileflag == 0); #  We have delayed gradient output until now if no files.
	      }
        }
        #
        # Read coordinates, forces, cell from auxilliary files even i
        # we found values in the .cst file.
        #
        if($gradflg ) {
    	    if ($cellfileflag ) {
    		($junk1, $junk2, $a, $b, $c, $aa, $ba, $ca) = split /\s+/,<CELL>;
    		$stress = <CELL>;
    		$estress = <CELL>;
                &ABCtoMAT($a, $b, $c, $aa, $ba, $ca, \@av, \@bv, \@cv);
   	    }
    	    if ($coordfileflag ) {
    		$junk = <COORDS>;
    		$natoms = scalar(@atomx);
    		for $iat (0..$natoms-1) {
    		   ($junk1, $atomxc[$iat], $atomyc[$iat], $atomzc[$iat]) = split /\s+/,<COORDS>;
    		}
		#
		# Convert Cartesian co-ordinates to fractional.
                #
		&CartToFrac(\@av,\@bv,\@cv, \@atomxc, \@atomyc, \@atomzc, 
                                            \@atomx, \@atomy, \@atomz);
    	    } 
    	    if ($forcefileflag ) {
    		$junk = <FORCES>;
    		$natoms = scalar(@atomx);
    		for $iat (0..$natoms-1) {
    		   ($junk1, $forcx[$iat], $forcy[$iat], $forcz[$iat]) = split /\s+/,<FORCES>;
    		}
    	    }
	  }
        # 
        # Write output. 
        #
        $outflag = 1 if ($gradflg && $icycle == 0);
        if ($outflag || $gradflg) {
	  &ABCtoMAT($a, $b, $c, $aa, $ba, $ca, \@av, \@bv, \@cv);
	}
        if ($outflag == 1 ) {
		&$begfunc(\@av, \@bv, \@cv, \@atomx, \@atomy, \@atomz, \@atype, 
                           $title, $box, 1 );
		$outflag++;
	}
        if ($gradflg && $toten != 0) {
		$natoms = scalar(@forcx);
		$gnorm = 0;
    		for $iat (0..$natoms-1) {
		   $gnorm += $forcx[$iat]*$forcx[$iat]+$forcy[$iat]*$forcy[$iat]+$forcz[$iat]*$forcz[$iat];
    		}
		$gnorm = sqrt($gnorm/$natoms) if $natoms > 0;
		$icycle++;
                &$filefunc($basename, $outfunc, \@av, \@bv, \@cv, 
                           \@atomx, \@atomy, \@atomz, \@atype, $title, $box, 
                           \@forcx, \@forcy, \@forcz, $icycle, $toten, $gnorm );
		$gradflg = 0;
		if (! $coordfileflag ) {
		  @atomx = @atomxn;@atomy = @atomyn;@atomz = @atomzn;
		}
        }
        #
        # Eigenvalues
        # 
        if( /^ \+\s*Electronic energies/ ... /^ =+ End of electronic energies =/ ) {
	  if (/^ \+\s*Electronic energies/) {
	    @eigen = ();
	    @occ = ();
	    $nbk = 0;
	  }
	  $nkpts = $1 if   (/^ \+ K-point # *(\d+)/);
			    #print "NKPTS: ",$nkpts,"\n";
	  if ( /^ \+ *\d+/ ) {
	    $eigen[$nbk] = $Fld[3];
	    $occ[$nbk] = $Fld[4];
	    $nbk++;
	  }
        }

    }
    &$endfunc($nbk,\@eigen, \@occ);
print STDERR "\n";
}

sub ReadNewtep {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype, $freq, $eigvecs, 
	$kptx, $kpty, $kptz, $wt, $title ) = @_;
    my ($a, $b, $c, $aa, $ba, $ca, $lvx, $lvy, $lvz);
    my (@Fld, $iatom, $coordflg, $nkpts, $junk, $kpflg);
    my ($junk1, $junk2, $junk3);
    my ($mode, $ion, $elem, $pspfile);
    my ($caa, $cba, $cca);

    #$verbose++;
    $fmt3="%16.10f%16.10f%16.10f\n";

    $coordflg = 0;
    $newtep_symmetry = 0;

    $have_cell_constraints = 0;
    $have_external_stress  = 0;

    while (<>) {
        chop;   # strip record separator
        @Fld = split ;

	#
	# ABC alpha,beta,gamma unit cell - don't use.
	#
        #$a = $1 , $aa = $2 if( /^ +a =  *($number) +(?:Free|Fixed)? +alpha = +($number)/);
        #$b = $1 , $ba = $2 if( /^ +b =  *($number) +(?:Free|Fixed)? +beta  = +($number)/);
        #$c = $1 , $ca = $2 if( /^ +c =  *($number) +(?:Free|Fixed)? +gamma = +($number)/);
	#
	# Title
	#
	if( /^ \** Title \**/ ) {
	  $$title = <>;
	  chomp $$title;
	  $_ = <>;
	}
	#
	# Unit cell vectors
	#
	if(/^\s+Real Lattice[(]A[)]\s+Reciprocal Lattice[(]1\/A[)]/ .. /^\s+Lattice parameters[(]A[)]/ ) {
	  if (/^(\s*$number){6}\s*$/ ){
	    ($lvx,$lvy,$lvz,$junk) = split; 
	    @$av=($lvx,$lvy,$lvz);
	    #print "A: ",$lvx," ",$lvy," ",$lvz,"\n";
	    $_=<>; ($lvx,$lvy,$lvz,$junk) = split; 
	    #print "B: ",$lvx," ",$lvy," ",$lvz,"\n";
	    @$bv=($lvx,$lvy,$lvz);
	    $_=<>; ($lvx,$lvy,$lvz,$junk) = split; 
	    #print "C: ",$lvx," ",$lvy," ",$lvz,"\n\n";
	    @$cv=($lvx,$lvy,$lvz);
	  }
	}
	#
	# Symmetry
	#
	if(/Number of symmetry operations = *(\d+)/ && $1 > 0) {
	  $newtep_symmetry=1;
	READSYM:{
	    $_ = &nextline;
	    while (! eof ) {
	      last READSYM unless ( /^\s+(\d+) rotation/ );
	      $_ = &nextline;
	      $newtep_symmetry = $1;
	      for $i (0..2) {
		last READSYM unless /^\s+\((\s*$number){3}\s*\)/;
		@Fld = split;
		($symop[$i][0],$symop[$i][1],$symop[$i][2]) = ($Fld[1],$Fld[2],$Fld[3]);
		$_ = &nextline;
	      }
	      last READSYM unless ( /^\s+(\d+) displacement/ );
	      $_ = &nextline;
	      last READSYM unless  /^\s+\((\s*$number){3}\s*\)/;
	      @Fld = split;
	      ($sym_disp[0],$sym_disp[1],$sym_disp[2])   = ($Fld[1],$Fld[2],$Fld[3]);
	      #
	      # Copy into global arrays
	      #
	      for $i (0..2) {
		$sym_ops[$newtep_symmetry][$i] = [@{$symop[$i]}];
	      }
	      $sym_disps[$newtep_symmetry] = [@sym_disp];

	      if( $verbose ) {
		print STDERR "Found Symmetry op",$newtep_symmetry,"\n";
		for $i (0..2) {
		  printf STDERR $fmt3, $sym_ops[$newtep_symmetry][$i][0],$sym_ops[$newtep_symmetry][$i][1],$sym_ops[$newtep_symmetry][$i][2];
		}
		printf STDERR $fmt3, $sym_disp[0],$sym_disp[1],$sym_disp[2];
		print STDERR "End Symmetry op",$newtep_symmetry,"\n";
	      }

	      $_ = &nextline; #  symmetry related atoms:
	      $_ = &nextline; #  Equiv atoms:

	      $_ = &nextline while (! eof && /: /);
	      $_ = &nextline while (! eof && /^ *$/);
	    }
	  }
	}
	#
	# Cell constraints
	#
	if( /^\s+Cell constraints are:/) {
	  $have_cell_constraints++;
	  ($junk1,$junk2,$junk3,@cell_constraints) = split;
	}
	#
	# External Pressure
	#
	if( m@^\s+External pressure/stress \(([^)]*)\)@ ) {
	  ($external_stress_unit) = $1;
	  $have_external_stress++;
	  $_ = <>;
	  @external_stress = split;
	  $_ = <>;
	  push @external_stress,split;
	  $_ = <>;
	  push @external_stress,split;
	}
	#
	# Atomic co-ordinates
	#
        if (/Element\s+Atom\s+Fractional coordinates/) {
            $iatom = 0;
            $coordflg = 1;
        }
        if ($coordflg > 0 && (/^\s+x-{58}x\s*$/ ... /^\s+x{60}\s*$/)) {
            if (/^\s+x\s+[A-Za-z]{1,2}\s+\d+(\s+$number){3}\s+x\s*/ ) {
                $$atomx[$iatom] = $Fld[3];
                $$atomy[$iatom] = $Fld[4];
                $$atomz[$iatom] = $Fld[5];
                $$atype[$iatom] = atom_type($Fld[1]);
                $iatom++;
            }
            $coordflg = 0 if /^\s+x{60}\s*$/;
        }
	#
	# Phonon Frequencies
	#
	if( (/^\s+\+ -{65} \+\s*$/ ... /^\s+={69}\s*$/)) {
	  if(  /^\s+\+\s+\d+\s+$number.*\+\s*$/ ) {
	    $$freq[$Fld[1]] = $Fld[2];
	  }
	}
	#
	# Phonon Eigenvectors
	#
	if (/^\s+Phonon Eigenvectors\s*$/ ... /^  ={69}\s*$/){
	  if (/^\s+Phonon Eigenvectors\s*$/) {
	  } elsif (/^\s+\d+\s+\d+(\s+$number){6}/) {
	    $mode = $Fld[0];
	    $ion  = $Fld[1];
	    $$eigvecs[$mode][$ion]=[$Fld[2],$Fld[3],$Fld[4],$Fld[5],$Fld[6],$Fld[7]];
	  }
	}
	#
	#  Snarf pseudopotential file names. Store in global
	#
	if( /^\s+Files used for pseudopotentials:\s*$/ .. /^\s*?$/ ) {
	  if(m@^\s+([A-Z]{1,2}) ([A-Z/][-\w_/]+)@i){
	    ($elem,$pspfile) = split;
	    $pspfiles{$elem} = $pspfile;
	  }
	}
        #
        #  Only record one block of special k-points.
        #
        if (/k-Points For BZ Sampling/ ) {
	  $kpflg++;
	  $nkpts = 0;
	}
	if( $kpflg && ( /^\s{13}\+{55}\s*$/ ... /^\s*$/)) {
	  if (/^\s+\+\s+\d+(\s+$number){4}\s+\+\s*$/) {
	    ($junk, $junk, $$kptx[$nkpts], $$kpty[$nkpts], $$kptz[$nkpts], $$wt[$nkpts], $junk) = split;
	    #
	    # Castep prints 6 figures.  Round to rational fraction if it's obvious
	    #
	    $$kptx[$nkpts] = round6($$kptx[$nkpts]);
	    $$kpty[$nkpts] = round6($$kpty[$nkpts]);
	    $$kptz[$nkpts] = round6($$kptz[$nkpts]);
	    $$wt[$nkpts]   = round6($$wt[$nkpts]);
	    $nkpts++;
	  }
	  $kpflg = 0 if (/^\s*$/);
        }
      }

    &CheckCellParameters( $av, $bv, $cv );

    #&ABCtoMAT($a, $b, $c, $aa, $ba, $ca, $av, $bv, $cv);
}

sub ReadNewtepPhonon {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype, $imass, 
	$freq, $eigvecs, $qptx, $qpty, $qptz, $wt ) = @_;

    my($x, $y, $z, $nions, $nmodes, $count, $atyp, $mymode, $mode, $ion, $myion);
    my (@q, @eigvec, @freqk, @xyz);

    #$verbose++;

    print "Entered ReadNewtepPhonon\n" if $verbose;
  @$atomx = ();    @$atomy = ();    @$atomz = (); @$atype = ();
  @$qptx = (); @$qpty = (); @$qptz = (); @$wt = ();
  @$eigvecs = ();
  while (<>) {
    chomp;
    $_ =~ s/\r$//;
    print "Processing \"$_\"\n" if $verbose;
    #
    # <>.phonon
    #
    $nions = $1 if /^ Number of ions\s*(\d+)/;
    $nmodes = $1 if /^ Number of branches\s*(\d+)/;
    if( /^ Unit cell vectors \(A(NG)?\)/) {
      print "Reading Cell Vectors\n" if $verbose;
      $_ = <>; @$av = split;
      $_ = <>; @$bv = split;
      $_ = <>; @$cv = split;
    }
    if( / Fractional Co-ordinates/../ end.*header/i) {
      print "Reading Co-ordinates\n" if $verbose;
      if( /^\s+\d+(\s+$fnumber){3}\s+[A-Za-z]{1,2}\s+$fnumber/ ) {
	($ion,$x,$y,$z,$atyp,$mass) = split;
	push @$atomx, $x;
	push @$atomy, $y;
	push @$atomz, $z;
	print " Atom $aty at $x,$y,$x\n" if $verbose;

	push @$atype, atom_type($atyp);
	push @$imass, $mass;
      }
    }
    #
    # Found start of block of frequencies
    #
    if (/^ +q-pt= +\d+ +($fnumber) *($fnumber) *($fnumber) ( *$fnumber){0,4} *$/) {
      print "Reading Frequencies\n" if $verbose;
      @q=($1,$2,$3);
      push @$qptx, $1;
      push @$qpty, $2;
      push @$qptz, $3;
      #print STDERR " ",$q[0]," ",$q[1]," ",$q[2];
      #print "   ";
      @freqk=();

      while (<>) {
	if (/^ +\d+ +($fnumber) /) {
	  push @freqk, $1;
	} else {
	  last;
	}
      }
      #$, = "  ";
      #print STDERR @freqk,"\n";
    }
    #
    # Found start of eigenvectors block
    #
    if (/^\s+Phonon Eigenvectors/) {
      print "Reading Eigenvectors\n" if $verbose;
      print STDERR "Q-pt  $#{$qpts} = ($q[0],$q[1],$q[2])\n" if $verbose;
      $_ = <>;
      @eigvec = ();
      #
      # Read in set of eigenvectors
      #
      for $mymode ( 0..$nmodes-1 ) {
#	$eigvec[$mode] = [0..$nions-1];
	for $myion ( 0..$nions-1 ) {
	  ($mode, $ion, @xyz) = split " ",<>;
	  $eigvec[$mode-1][$ion-1] = [@xyz];
	}
      }
      push @$freq, [@freqk];
      push @$eigvecs, [@eigvec];
    }
  }
}

#
#  Read a "<seedname>.cell" for new CASTEP
#  This version reads only structure kpoints and phonon qpoints
#
sub ReadNewtepCell {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype,
	$kptx, $kpty, $kptz, $wt, $pkptx, $pkpty, $pkptz, $pwt ) = @_;
    my( @atomxc, @atomyc, @atomzc );
    my (@symop, @sym_disp);
    my @Fld;
    my($iatom,$ikpt,$ipkpt, $atyp,$abcflg,$cartflag) = (0,0,0,0,0,0);
    my ($lvx, $lvy, $lvz, $junk);
    my ($a, $b, $c, $alpha, $beta, $gamma);
    my ($elem, $pspfile);
    my $asym = "";

#    $verbose++;

    $fmt3="%16.10f%16.10f%16.10f\n";
    $newtep_symmetry = 0;
    @external_stress = ();

    while (&nextline) {

      if ( /^\s*%block\s*lattice_cart\s*$/i .. /^\s*%endblock\s*lattice_cart\s*$/i) {
	$abcflg=0;
	if (/^\s*(\s*$number){3}\s*$/ ){
	  ($lvx,$lvy,$lvz,$junk) = split;
	  @$av=($lvx,$lvy,$lvz);
	  $_=&nextline; ($lvx,$lvy,$lvz,$junk) = split;
	  @$bv=($lvx,$lvy,$lvz);
	  $_=&nextline; ($lvx,$lvy,$lvz,$junk) = split;
	  @$cv=($lvx,$lvy,$lvz);
	}
      }
      if ( /^\s*%block\s*lattice_abc\s*$/i .. /^\s*%endblock\s*lattice_abc\s*$/i) {
	$abcflg++;
	if (/^\s*(\s*$number){3}\s*$/ ){
	  ($a,$b,$c,$junk) = split;
	  $_=&nextline; ($alpha,$beta,$gamma,$junk) = split;
	}
      }

      if ( /^\s*%block\s*positions_frac\s*$/i .. /^\s*%endblock\s*positions_frac\s*$/i) {
	if (/^\s*[A-Za-z]{1,2}[:\d]*\s*(\s*$number){3}\s*((SPIN|MAGMOM)\s*=\s*$number)?\s*$/i ){
	  @Fld = split;
	  $$atomx[$iatom] = $Fld[1];
	  $$atomy[$iatom] = $Fld[2];
	  $$atomz[$iatom] = $Fld[3];
	  $SPIN[$iatom] = $1 if(  /SPIN\s*=\s*($number)/ );

	  $$atype[$iatom] = atom_type($Fld[0]);
	  $iatom++;
	}
	$cartflag = -1;
      }

      if ( /^\s*%block\s*positions_abs\s*$/i .. /^\s*%endblock\s*positions_abs\s*$/i) {
	if (/^\s*[A-Za-z]{1,2}[:\d]*\s*(\s*$number){3}\s*((SPIN|MAGMOM)\s*=\s*$number)?\s*$/i ){
	  @Fld = split;
	  $atomxc[$iatom] = $Fld[1];
	  $atomyc[$iatom] = $Fld[2];
	  $atomzc[$iatom] = $Fld[3];
	  $SPIN[$iatom] = $1 if(  /SPIN\s*=\s*($number)/ );

	  $$atype[$iatom] = atom_type($Fld[0]);
	  $iatom++;
	}
	$cartflag = 1;
      }

      #
      #  Snarf pseudopotential file names. Store in global
      #
      if( /^\s*%block\s*species_pot\s*$/i .. /^\s*%endblock\s*species_pot\s*$/i ) {
	if(m@^\s*([A-Z]{1,2})\s+([A-Z/][\w./]+)@i){
	  ($elem,$pspfile) = split;
	  $pspfiles{$elem} = $pspfile;
	}
      }

      if ( /^\s*%block\s*kpoints_list\s*$/i .. /^\s*%endblock\s*kpoints_list\s*$/i) {
	if (/^(\s*$number){4}\s*$/ ){
	  @Fld = split;
	  $$kptx[$ikpt] = $Fld[0];
	  $$kpty[$ikpt] = $Fld[1];
	  $$kptz[$ikpt] = $Fld[2];
	  $$wt[$ikpt]   = $Fld[3];
	  $ikpt++;
	}
      }
      #$, = " " ;
      if ( /^\s*%block\s*phonon_kpoint_list\s*$/i .. /^\s*%endblock\s*phonon_kpoint_list\s*$/i) {
	if (/^(\s*$number){3,4}\s*$/ ){
	  @Fld = split;
	  $$pkptx[$ipkpt] = $Fld[0];
	  $$pkpty[$ipkpt] = $Fld[1];
	  $$pkptz[$ipkpt] = $Fld[2];
	  $$pwt[$ipkpt]   = $Fld[3];
	  $ipkpt++;
	}
      }
      if ( /^\s*symmetry_generate\b/ ) {
	$newtep_symmetry=1;
	print STDERR "Found Symmetry_generate",$newtep_symmetry,"\n" if $verbose;
      }
      #
      # TODO: Finish the read and handling of these blocks.
      #
      if ( /^\s*%block\s*symmetry_ops\s*$/i .. /^\s*%endblock\s*symmetry_ops\s*$/i) {
	if (/^(\s*$number){3}\s*$/ ){
	  $newtep_symmetry++;
	  ($symop[0][0],$symop[0][1],$symop[0][2]) = split;
	  $_ = &nextline;
	  ($symop[1][0],$symop[1][1],$symop[1][2]) = split;
	  $_ = &nextline;
	  ($symop[2][0],$symop[2][1],$symop[2][2]) = split;
	  $_ = &nextline;
	  ($sym_disp[0],$sym_disp[1],$sym_disp[2]) = split;
	  for $i (0..2) {
	    $sym_ops[$newtep_symmetry][$i] = [@{$symop[$i]}];
	  }
	  $sym_disps[$newtep_symmetry] = [@sym_disp];

	  if( $verbose ) {
	    print STDERR "Found Symmetry op",$newtep_symmetry,"\n";
	    for $i (0..2) {
	      printf STDERR $fmt3, $sym_ops[$newtep_symmetry][$i][0],$sym_ops[$newtep_symmetry][$i][1],$sym_ops[$newtep_symmetry][$i][2];
	    }
	    printf STDERR $fmt3, $sym_disp[0],$sym_disp[1],$sym_disp[2];
	    print STDERR "End Symmetry op",$newtep_symmetry,"\n";
	  }
	}
      }
      #
      # External Pressure
      #
      if ( /^\s*%block\s*external_pressure\s*$/i .. /^\s*%endblock\s*external_pressure\s*$/i) {
	$have_external_stress++;
	if( m/^\s*([A-Za-z]+)\s*$/ ) {
	  ($external_stress_unit) = $1;
	} elsif ( /(\s+$number){3}/ ) {
	  @external_stress = split;
	}elsif ( /(\s+$number){1,2}/ ) {
	  push @external_stress,split;
	}
      }
      #
      # Cell Constraints
      #
      if ( /^\s*%block\s*cell_constraints\s*$/i .. /^\s*%endblock\s*cell_constraints\s*$/i) {
	if ( /^\s*\d\s+\d\s+\d$/ ) {
	  @cell_constraints = split;
	  $_ = <>;
	  @cell_constraints = (@cell_constraints, split);
	  $have_cell_constraints = 1;
	}
      }
      #
      # Fix_all_cell
      #
      if( /^\s*fix_all_cell\s*[:=]?\s*t/i) {
	$fix_all_cell = 1;
      }
    }
    &ABCtoMAT($a, $b, $c, $alpha, $beta, $gamma, $av, $bv, $cv) if $abcflg;

    &CheckCellParameters( $av, $bv, $cv );

    &CartToFrac($av,$bv,$cv, \@atomxc, \@atomyc, \@atomzc, 
		$atomx, $atomy, $atomz) if $cartflag > 0 ;

    print STDERR "Found ",$newtep_symmetry," symmetry operations\n" if $verbose;
  }
#
# Read Geom Opt/MD from a newtep GEOM file.
# Extract *all* sets of atomic co-ords and call supplied
# function repeatedly to handle the extracted co-ordinates.
#
our ($nframes);

sub ReadNewtepGeom{
  my ($begfunc, $filefunc, $outfunc, $endfunc, $basename, $box) = @_;

  my ($iter, $cycle, $atyp, $x,$y,$z, $hec, $hrow, $natoms,$gnorm);
  my(@av, @bv, @cv, @atomx, @atomy, @atomz, @forcx, @forcy, @forcz, @atype, @energy,@Fld);

  open INPUT,"<$ARGV[0]" or die "Failed to open $ARGV[0] for reading\n";
  $nframes = CountNewGeomFrames(INPUT);

  seek INPUT,0,0;

  $debug = 0;

  $iter = 0;
  $hrow = 0;
  LINE: while ( <INPUT> ) {
    chomp;
    @Fld = split;

use Cwd 'abs_path';
    if( /^ BEGIN header/.../^ END header/ ) {
use Cwd 'abs_path';
      $title = $_ if ! /^ (BEGIN|END) header/;
      printf STDERR "Reading header $iter\n" if $debug;
      $title = "Converted from CASTEP md/geom output by CETEPROUTS" if $title=~/^\s*$/;
    } elsif( /<-- R/ ) {
      printf STDERR "Adding atom %s - n=%d\n",$Fld[0],2+$#atype if $debug;
      push @cartx,$abohr*$Fld[2];
      push @carty,$abohr*$Fld[3];
      push @cartz,$abohr*$Fld[4];
      push @atype,atom_type($Fld[0]);

      $nat_cnt ++;
    } elsif( /<-- F/ ) {
      push @forcx,$Fld[2];
      push @forcy,$Fld[3];
      push @forcz,$Fld[4];
      
    } elsif( /<-- h/) {
      $vec = \@av if( $hrow == 0);
      $vec = \@bv if( $hrow == 1);
      $vec = \@cv if( $hrow == 2);

      push @$vec, $abohr*$Fld[0],$abohr*$Fld[1],$abohr*$Fld[2];

      if( $debug && $hrow == 2) {
        printf STDERR "%10.3f %10.3f %10.3f\n",$av[0],$av[1],$av[2];
        printf STDERR "%10.3f %10.3f %10.3f\n",$bv[0],$bv[1],$bv[2];
        printf STDERR "%10.3f %10.3f %10.3f\n",$cv[0],$cv[1],$cv[2];
        print STDERR "\n";
      }
      $hrow++;
    } elsif( /<-- E/) {
      $toten = $Fld[0];
      push @energy, $Fld[0];
    } elsif  (/^\s+$number$/) {
	$cycle = $Fld[0];                # Found a new set of co-ordinates
	$iter++;
	printf STDERR "Reading Block $iter ($cycle)\n" if $debug;
	@cartx = (); @carty = (); @cartz = (); @atype = ();
	@forcx = (); @forcy = (); @forcz = (); 
	@av = (); @bv = (); @cv = ();
    } elsif ( /^\s*$/) {
      if ( $iter > 0 ) {
	&CheckCellParameters( \@av, \@bv, \@cv );
	@atomx = (); @atomy = (); @atomz = ();
	&CartToFrac(\@av,\@bv,\@cv,\@cartx,\@carty,\@cartz,\@atomx,\@atomy,\@atomz);
      }
      &$begfunc(\@av, \@bv, \@cv, \@atomx, \@atomy, \@atomz, \@atype, $box, $title, 1) if ($iter == 1);
      printf STDERR "End of Block $iter ($cycle)\n" if $debug;
      $hrow = 0;
      $nat_cnt  = 0;

      next LINE unless $iter > 0;

      $natoms = scalar(@forcx);
      $gnorm = 0;
      for $iat (0..$#forcx) {
	$gnorm += $forcx[$iat]*$forcx[$iat]+$forcy[$iat]*$forcy[$iat]+$forcz[$iat]*$forcz[$iat];
      }
      $gnorm = sqrt($gnorm/$natoms) if $natoms > 0;
      &$filefunc($basename, $outfunc, \@av, \@bv, \@cv, 
                           \@atomx, \@atomy, \@atomz, \@atype, $title, $box, 
                           \@forcx, \@forcy, \@forcz, $iter, $toten, $gnorm );

    }
    @atomx = ();
  }
 finished:
  if( $#atomx >= 0) {
    &CheckCellParameters( \@av, \@bv, \@cv );
    &CartToFrac(\@av,\@bv,\@cv,\@cartx,\@carty,\@cartz,\@atomx,\@atomy,\@atomz);
    &$filefunc($basename, $outfunc, \@av, \@bv, \@cv, 
	       \@atomx, \@atomy, \@atomz, \@atype, $box, 
	       \@forcx, \@forcy, \@forcz, $iter, $toten, $gnorm );
  }
  &$endfunc();
}

#
#
#

sub readf77rec {
    my $fh = shift;
    my $datatype = shift;

    my %datalen = ('f',4,'d',8,'i',4,'I',4,'l',4,'L',4);
    my ($rec, $reclen, $recl, $reclene, $num);
    $, = " ";

    read $fh, $recl, 4;
    $reclen = unpack "I", $recl;
    return () if $reclen <= 0;
    read $fh, $rec, $reclen;
    return () if eof ($fh);
    read $fh, $recl, 4;
    $reclene = unpack "I", $recl;
    return () unless $reclen == $reclene;
    $num = $reclen / $datalen{$datatype};
    return (unpack "$datatype$num", $rec);
}

#
#  Read CASTEP fort.13 or CETEP fort.3 or Cerius 2  CASTEP .gm files.
#  Doesn't really work since there's not enough info to determine atom types,
#  or even numbers of atoms of each type.
#
sub ReadFort13 {
    my ($av, $bv, $cv, $atomx, $atomy, $atomz, $atype, $kptx, $kpty, $kptz, $wt ) = @_;
    my @data;
    my ($i,$nat, $nkptr);

    open FILE,$ARGV[0] or die "Failed to open $ARGV[0]\n";

    #
    # First record contains unit cell vectors. Skip 3-6
    #

    @data = readf77rec(\*FILE,'d');
    return if @data != 9;
    foreach $i ( (0,1,2) ) {
         $$av[$i] = shift @data; 
         $$bv[$i] = shift @data;
         $$cv[$i] = shift @data;
    }
    @data = readf77rec(\*FILE,'d');
    print STDERR "Volc = $data[0]\n";
    @data = readf77rec(\*FILE,'d'); # RECC - throw away
    @data = readf77rec(\*FILE,'d'); # DIRI - throw away
    @data = readf77rec(\*FILE,'d'); # POSIOL - throw away
    @data = readf77rec(\*FILE,'d'); # POSION
    $nat = @data / 3;
    while (scalar(@data) > 0) {
         push @$atomx, shift @data;
         push @$atomy, shift @data;
         push @$atomz, shift @data;
    }
    
    @data = readf77rec(\*FILE,'d'); # RMOVE - throw away
    @data = readf77rec(\*FILE,'d'); # CELEN - throw away
    @data = readf77rec(\*FILE,'d'); # VKPT
    while (scalar(@data) > 0) {
         push @$kptx, shift @data;
         push @$kpty, shift @data;
         push @$kptz, shift @data;
    }
    @data = readf77rec(\*FILE,'d'); # WTKPT
    $nkptr = @data;
    while (scalar(@data) > 0) {
         push @$wt, shift @data;
    }
} 

sub SuperCell {
    #
    # Apply periodic boundary conditions and generate periodic
    # images of atoms within the supercell with vectors in @supercell
    # Return a list of the translations to be applied to each atom.
    #
    my ($atomx, $atomy, $atomz, $atype, $supercell) = @_;

    my ($iat, $ish, $jsh, $ksh);
    my ($posx, $posy, $posz);
    my (@shat, @shlist);

    #
    # Currently only supports diagonal supercells.
    #
    my (@box) = (0, $$supercell[0],0, $$supercell[4],0, $$supercell[8]);

    foreach $iat (0 .. scalar(@$atomx)-1) {
        @shat = ();
        foreach $ish (floor($box[0]) .. ceil($box[1]) ) {
            $posx = fmod($$atomx[$iat],1.0)+$ish;
            if( $posx >= $box[0] && $posx < $box[1] ) {
                foreach $jsh (floor($box[2]) .. ceil($box[3]) ) {
                    $posy = fmod($$atomy[$iat],1.0)+$jsh;
                    if ($posy >= $box[2] && $posy < $box[3]) {
                        foreach $ksh (floor($box[4]) .. ceil($box[5]) ) {
                            $posz = fmod($$atomz[$iat],1.0)+$ksh;
                            if ($posz >= $box[4] && $posz < $box[5] ) {
#                               print STDERR "$ish $jsh $ksh   $posx   $posy   $posz";
#                               print STDERR " accepted\n";
                                #
                                # A bit complicated but the idea is to create
                                # a list of (references to, one per atom) 
                                # lists containing the shift operations.
                                push @shat, [$posx-$$atomx[$iat],
                                             $posy-$$atomy[$iat],
                                             $posz-$$atomz[$iat]];
#                               print STDERR @shat,"\n";
                            }
                        }
                    }
                }
            }
        }
        # 
        # Add the list of translations for this atom in @shat
        # to the big atom list.  Must be careful to add a
        # reference to an anonymous *copy* of @shat rather
        # than @shat itself since we reuse it!
        push @shlist, [@shat];
    }
    return @shlist;
}

sub ExpandedCell {
    #
    # Apply periodic boundary conditions and generate periodic
    # images of atoms within specified planes in @box.
    # Return a list of the translations to be applied to each atom.
    #
    my ($atomx, $atomy, $atomz, $atype, $box) = @_;

    my ($iat, $ish, $jsh, $ksh);
    my ($posx, $posy, $posz);
    my (@shat, @shlist);

    foreach $iat (0 .. scalar(@$atomx)-1) {
        @shat = ();
        foreach $ish (floor($$box[0]) .. ceil($$box[1]) ) {
            $posx = fmod($$atomx[$iat],1.0)+$ish;
            if( $posx >= $$box[0] && $posx < $$box[1] ) {
                foreach $jsh (floor($$box[2]) .. ceil($$box[3]) ) {
                    $posy = fmod($$atomy[$iat],1.0)+$jsh;
                    if ($posy >= $$box[2] && $posy < $$box[3]) {
                        foreach $ksh (floor($$box[4]) .. ceil($$box[5]) ) {
                            $posz = fmod($$atomz[$iat],1.0)+$ksh;
                            if ($posz >= $$box[4] && $posz < $$box[5] ) {
#                               print STDERR "$ish $jsh $ksh   $posx   $posy   $posz";
#                               print STDERR " accepted\n";
                                #
                                # A bit complicated but the idea is to create
                                # a list of (references to, one per atom) 
                                # lists containing the shift operations.
                                push @shat, [$posx-$$atomx[$iat],
                                             $posy-$$atomy[$iat],
                                             $posz-$$atomz[$iat]];
#                               print STDERR $posx-$$atomx[$iat]," ",
#                                            $posy-$$atomy[$iat]," ",
#                                            $posz-$$atomz[$iat],"\n";
                            }
                        }
                    }
                }
            }
        }
        # 
        # Add the list of translations for this atom in @shat
        # to the big atom list.  Must be careful to add a
        # reference to an anonymous *copy* of @shat rather
        # than @shat itself since we reuse it!
        push @shlist, [@shat];
    }
    return @shlist;
}

sub Expand {
    #
    # Apply list of pbc atom replications determined by ExpandedCell
    #
     my ($atomx, $atomy, $atomz, $atype, $shlist,
         $atomxo, $atomyo, $atomzo, $atypeo) = @_;
     my (@shat, $sh, $iat, $shat);

     $, = "  ";
     @$atomxo = ();
     @$atomyo = ();
     @$atomzo = ();
     @$atypeo = ();
     $iat=0;

     foreach $shat (@$shlist) {
#        print STDERR "Atom: $iat ",scalar(@$shat),"images";
         foreach $sh (@$shat) {
#            print STDERR "    ",$$sh[0],$$sh[1],$$sh[2];
             push @$atomxo, $$atomx[$iat]+$$sh[0];
             push @$atomyo, $$atomy[$iat]+$$sh[1];
             push @$atomzo, $$atomz[$iat]+$$sh[2];
             push @$atypeo, $$atype[$iat];
         }
#        print STDERR "\n";
	$iat++;

     }
}

sub ExpandPerturbation {
    #
    # Apply list of pbc atom replications determined by ExpandedCell
    # to expand a *perturbation* vector.  Assume that result is real
    # (but check)
    #
     my ($qptx, $qpty, $qptz, $pertx_r, $perty_r, $pertz_r, 
	 $pertx_i, $perty_i, $pertz_i, $shlist,
         $pertxo, $pertyo, $pertzo) = @_;
     my (@shat, $sh, $iat, $shat,$phase, $cosph,$sinph);
     my( $imtol) = (0.001);

     $, = "  ";
#     $verbose++;
     @$pertxo = ();
     @$pertyo = ();
     @$pertzo = ();
     print STDERR "Q=(",$qptx, ",",$qpty, ",",$qptz,")\n" if $verbose;
     foreach $shat (@$shlist) {
       print STDERR "Pert: $iat ",scalar(@$shat),"images" if $verbose;
       foreach $sh (@$shat) {
	 $phase = $qptx*$$sh[0] + $qpty*$$sh[1] + $qptz*$$sh[2];
	 $cosph = cos($twopi*$phase); $sinph = sin($twopi*$phase); 
	 print STDERR "    ",$$sh[0],$$sh[1],$$sh[2],$phase,"\n" if $verbose;
	 
	 push @$pertxo, $cosph*$$pertx_r[$iat] - $sinph*$$pertx_i[$iat];
	 push @$pertyo, $cosph*$$perty_r[$iat] - $sinph*$$perty_i[$iat];
	 push @$pertzo, $cosph*$$pertz_r[$iat] - $sinph*$$pertz_i[$iat];
       }
       $iat++;
     }
     print STDERR "Exiting ExpandPerturbation with $#{$pertxo} atoms\n" if $verbose;
}

###########################################################################
# ELECTRON DENSITY readers and writers
###########################################################################
#
# Read Newtep formatted electron density
#
sub ReadNewtepDen {
  my ($den, $nx, $ny, $nz) = @_;
  my( $i, $j, $k, $rhor, $rhoi);
###  my( @denz);
  #
  # Assume a complex charge density
  #
  $$nx = $$ny = $$nz = 0;
  while( <> ) {
use Cwd 'abs_path';
    if ( ! ( / BEGIN header/ ... / END header/)  && ! /^ *$/) {
      $rhor = $rhoi = 0.0;
      ($i,$j,$k,$rhor,$rhoi) = split;
      
      $$nx = $i if( $i > $$nx);
      $$ny = $j if( $j > $$ny);
      $$nz = $k if( $k > $$nz);
      #  printf STDERR "%6d %6d %6d %12.5f\n",$i,$j,$k,$rhor;
      $i--; $j--;$k--;
      ###    $denz[$i][$j][$k] = $rhor + i*$rhoi;
      $$den[$i][$j][$k] = $rhor;
    }
  }
  #
  # Attempt to generate a real density from a complex one assuming that
  # n(r) = |n(r)| exp (-i*r) is a smooth function.
  #
###  $sign = 1.0;
###  for( $i=1; $i < $$nx; $i++) {
###    for( $j,1; $j < $$ny; $j++) {
###      $iqz = arg($denz[$i][$j][0] * ~$denz[$i][$j][1] );
###      for( $k=2; $k < $$nz; $k++) {
###	$rhor = abs($denz[$i][$j][$k]);
###	$iqz2 = arg($denz[$i][$j][$k] * ~$denz[$i][$j][$k-1] );
###	if( fabs($iqz2-$iqz) > 0.5*$pi && fabs($iqz2-$iqz) < 1.5*$pi ) {
###	  $sign = -$sign;
###	}
###	$$den[$i][$j][$k] = $sign * $rhor;
###	$iqz = $iqz2;
###      }
###    }
###  }

}

#
#
# Write XPLOR format electron density map file
#
sub Write_Xplor {
  my ($nx,$ny,$nz,$a,$b,$c,$alpha,$beta,$gamma,$title,$den) = @_;
  my ($i, $j, $k, $nc, $now_string);

  $now_string = strftime "%a %b %e %H:%M:%S %Y", gmtime;

  print "\n     2\n";
  print $title,"\n";
  print "Date: $now_string\n\n\n";

  printf "%8d%8d%8d%8d%8d%8d%8d%8d%8d\n",$nx,1,$nx,$ny,1,$ny,$nz,1,$nz;
  printf "%12.5f%12.5f%12.5f%12.5f%12.5f%12.5f\n",$a,$b,$c,$alpha,$beta,$gamma;

  print "ZYX\n";

  for ($k = 0; $k < $nz; $k++) {
    $nc = 0;
    printf "%8d\n",$k;
    for ($i = 0; $i < $nx; $i++) {
      for ($j = 0; $j < $ny; $j++) {
	printf "%12.5f",$$den[$i][$j][$k];
	$nc++;
	if( $nc == 6 ) {
	  $nc = 0;
	  print "\n";
	}
      }
    }
    print "\n" if $nc > 0;
  }
  printf "%8d\n%12.4f %12.4f\n",-9999,0.0,0.0;
}
#
# Write Materials Studio .grd format electron density map file
#
sub Write_grd {
  my ($nx,$ny,$nz,$a,$b,$c,$alpha,$beta,$gamma,$title,$den) = @_;
  my ($i, $j, $k, $nc, $now_string);

  $now_string = strftime "%a %b %e %H:%M:%S %Y", gmtime;

  print $title,"\n";
  print "(E12.5)\n";

  printf "%12.5f%12.5f%12.5f%12.5f%12.5f%12.5f\n",$a,$b,$c,$alpha,$beta,$gamma;
  printf "%8d%8d%8d\n",$nx-1,$ny-1,$nz-1;
  printf "%8d%8d%8d%8d%8d%8d%8d\n",1,0,$nx-1,0,$ny-1,0,$nz-1;

  for ($i = 0; $i < $nx; $i++) {
    for ($k = 0; $k < $nz; $k++) {
      for ($j = 0; $j < $ny; $j++) {
	printf "%12.5f\n",$$den[$i][$j][$k];
      }
    }
    print "\n" if $nc > 0;
  }
}

1;
