###############################################################################
################### MOOSE Application Standard Makefile #######################
###############################################################################
#
# Optional Environment variables
# MOOSE_DIR        - Root directory of the MOOSE project
# HERD_TRUNK_DIR   - Location of the HERD repository
# FRAMEWORK_DIR    - Location of the MOOSE framework
#
###############################################################################
MODULE_DIR         ?= $(shell dirname `pwd`)
MOOSE_DIR          ?= $(shell dirname $(MODULE_DIR))
FRAMEWORK_DIR      ?= $(MOOSE_DIR)/framework
ADDITIONAL_CPPFLAGS += -Wall -Wextra
###############################################################################

# framework
include $(FRAMEWORK_DIR)/build.mk
include $(FRAMEWORK_DIR)/moose.mk

# Module
MODULE_NAME := stochastic_tools
include $(MODULE_DIR)/modules.mk

###############################################################################
# Additional special case targets should be added here

# BUILD MLPACK
#
# (1) Create a conda environment
#
#     conda create -n mlpack --no-default-packages
#     conda install boost moose-petsc cmake
#
# (2) Build libMesh with boost
#
#     conda env config vars set LIBMESH_ROOT=/Users/slauae/projects/libmesh LIBMESH_DIR=/Users/slauae/projects/libmesh/libmesh-clang
#     conda activate mlpack
#     conda env config vars list
#     cd ~/projects/libmesh
#     libmesh.sh --with-boost (this is my own script)
#
# (3) Build armadillo
#
#     cd projects
#     git clone https://gitlab.com/conradsnicta/armadillo-code.git
#     cd armadillo-code
#     cmake .
#     make -j 12
#
# (4) Build mlpack
#
#     cd projects
#     git clone https://github.com/mlpack/mlpack.git
#     cd mlpack
#     mkdir build
#     cd build
#     cmake .. -DBUILD_PYTHON_BINDINGS=OFF -DARMADILLO_INCLUDE_DIR=/Users/slauae/projects/armadillo-code/include -DARMADILLO_LIBRARY=/Users/slauae/projects/armadillo-code -DBUILD_CLI_EXECUTABLES=OFF -DBUILD_TESTS=OFF -DCMAKE_INSTALL_PREFIX=/Users/slauae/projects/mlpack/install
#     make -j $MOOSE_JOBS
#     make install

mlpack_DIR = /Users/slauae/projects/mlpack/install
mlpack_INCLUDE = $(mlpack_DIR)/include
mlpack_LIB = $(mlpack_DIR)/lib

ADDITIONAL_INCLUDES += -I$(mlpack_INCLUDE)
ADDITIONAL_LIBS     += -L$(mlpack_LIB) -lmlpack-$(METHOD)
#$(info $(mlpack_INCLUDE))
#$(info $(ADDITIONAL_INCLUDES))
