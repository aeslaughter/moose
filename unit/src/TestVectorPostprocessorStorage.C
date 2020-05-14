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
  auto ptr = std::make_unique<VectorPostprocessorVectorState<int>>();
  ptr->is_distributed = true;
  ptr->old = &vec_int;
  ptr->current = &vec_int;

  VectorPostprocessorStorage storage;
  storage._vectors.emplace_back(std::move(ptr));

  auto & back = static_cast<VectorPostprocessorVectorState<int> &>(*storage._vectors.back());
  // back.is_distributed = true;
  // back.old = &vec_int;
  // back.current = &vec_int;

  EXPECT_TRUE(back.is_distributed);
  EXPECT_EQ(*back.current, vec_int);
  EXPECT_EQ(back.current, &vec_int);
}
