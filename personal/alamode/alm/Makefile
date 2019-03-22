.SUFFIXES: .h .cpp
#-----------------------------------------------
# Makefile for the program 'ALM'.
# Please modify the variables properly.
# We recommend to use Intel c++ compiler.
#-----------------------------------------------

CXX = icpc 
CXXFLAGS = -O2 -xHOST -openmp -std=c++11
INCLUDE = -I../include -I/home/z8j/softwares/eigen-3.3.4/Eigen -I/software/dev_tools/swtree/cs400_centos7.2_pe2016-08/boost/1.61.0/centos7.2_gnu5.3.0/include/boost

CXXL = ${CXX}
LDFLAGS = -mkl

LAPACK = 
LIBS = ${LAPACK}

#-----------------------------------------------
# General rules 
#-----------------------------------------------

.cpp.o:
	${CXX} ${CXXFLAGS} ${INCLUDE} -c $<

PROG = alm

CXXSRC= alamode.cpp constraint.cpp error.cpp fcs.cpp files.cpp \
	fitting.cpp input.cpp interaction.cpp main.cpp memory.cpp \
	patterndisp.cpp symmetry.cpp system.cpp timer.cpp writes.cpp 

OBJS= ${CXXSRC:.cpp=.o}

default: alm

all: ${PROG}

alm: ${OBJS}
	${CXXL} ${LDFLAGS} -o $@ ${OBJS} ${LIBS}

clean:
	rm -f ${OBJS}

.PHONY: clean

depend:
	gcc -MM *.cpp > .depend

-include .depend
