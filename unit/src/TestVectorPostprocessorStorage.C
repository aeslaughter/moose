//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#include "gtest/gtest.h"
#include "VectorPostprocessorStorage.h"

TEST(VectorPostprocessorStorage, StateBase)
{
  // Real
  std::vector<Real> vec_real = {1.1, 2.1};
  VectorPostprocessorVectorState<Real> state_real;
  state_real.current = &vec_real;

  // int
  std::vector<int> vec_int = {2011, 2013};
  VectorPostprocessorVectorState<int> state_int;
  state_int.current = &vec_int;

  // VectorPostprocessorStorage storage;
  // storage._values.emplace_back("int",
}
