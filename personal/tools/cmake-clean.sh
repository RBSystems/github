#!/bin/bash
# program: to clean cmake/make cache files

# files to be removed
rmg_trash="
CMakeCache.txt
CPackConfig.cmake
CPackSourceConfig.cmake
Makefile
cmake_install.cmake
CMakeFiles
*/lib*.a
*/Makefile
*/CMakeFiless
*/cmake_install.cmake
*/*/Makefile
*/*/lib*.a
*/*/CMakeFiless
*/*/cmake_install.cmake
"

#################################################
# Following lines should not be modified
#################################################

function rmg_clean()
{
    if [ -e $* ]; then
        rm -rf $*
#        ls -l $*
        echo -e "\n$* removed.\n"
    fi
}

echo "RMG cmake/make cleaning..."

for tmp in $rmg_trash
do
    rmg_clean $tmp
done

exit 0
