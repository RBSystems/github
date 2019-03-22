#!/usr/bin/env perl

#
# Read Cerius2 Castep ".cst" and supplementary .coords, .cell .force files
# and convert to form for "viewmol".
# Install as viewmol input  filter in "viewmolrc", eg:
#       option castep $HOME/cteprouts/cst2vmol %s "Welcome to CASTEP"
#       output geom $HOME/cteprouts/vmol2geom %s

#    Copyright (c) Keith Refson 1998-2012
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

use Cwd 'abs_path';
BEGIN {$mypath = $0;
       $mypath = abs_path($mypath);
       if ($mypath =~ /^[A-Za-z]:/) {$mypath =~ s@[^\\]+$@@; } else {$mypath =~ s@[^/]+$@@;}
     }
use lib "$mypath";
use ceteprouts;

if ( $ARGV[0] eq "-b" && $#ARGV > 5 ) {
    shift @ARGV;
    while ($#box < 5 ) {
	push @box, shift @ARGV;
    }
}

ReadNewtepGeom (\&NullFunc, \&NoName, \&WriteXYZ, 
                \&NullFunc, $ARGV[0], \@box);
