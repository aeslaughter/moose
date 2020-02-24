//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html
#include "gtest/gtest.h"
#include <vector>
#include <iterator>
#include "skip_iterator.h"
#include "Calculators.h"
#include "libmesh/communicator.h"
#include "libmesh/parallel_object.h"

using namespace StochasticTools;

TEST(Calculators, skip_iterator)
{
  std::vector<int> x = {0, 1, 2, 3, 4, 5, 6, 7};

  // default-constructible
  {
    skip_iterator<const int> iter = make_skip_iterator<const int>(x.begin(), 3);
    EXPECT_EQ(*iter, 0);
  }

  // copy-constructable
  {
    skip_iterator<int> iter1 = make_skip_iterator<int>(x.begin(), 3);
    skip_iterator<int> iter2(iter1);
    EXPECT_EQ(*iter1, 0);
    EXPECT_EQ(*iter2, 0);
    EXPECT_TRUE(iter1 == iter2);
  }

  // copy-assignable
  {
    skip_iterator<int> iter1 = make_skip_iterator<int>(x.begin(), 3);
    StochasticTools::skip_iterator<int> iter2 = iter1;
    EXPECT_EQ(*iter1, 0);
    EXPECT_EQ(*iter2, 0);
    EXPECT_TRUE(iter1 == iter2);
  }

  // Compare
  {
    skip_iterator<int> iter1 = make_skip_iterator<int>(x.begin(), 3);
    StochasticTools::skip_iterator<int> iter2(iter1);
    EXPECT_TRUE(iter1 == iter2);
    iter2++;
    EXPECT_FALSE(iter1 == iter2);
    iter1++;
    EXPECT_TRUE(iter1 == iter2);
  }

  // Dereferenced
  {
    skip_iterator<int> iter1 = make_skip_iterator<int>(x.begin() + 1, 3);
    EXPECT_EQ(*iter1, 1);
  }

  // Mutable
  {
    skip_iterator<int> iter1 = make_skip_iterator<int>(x.begin() + 1, 3);
    *iter1 = 1980;
    EXPECT_EQ(*iter1, 1980);
    EXPECT_EQ(x[0], 0);
    EXPECT_EQ(x[1], 1980);
    iter1++;
    iter1++;
    iter1++;
    EXPECT_EQ(*iter1, 5);
    *iter1 = 1949;
    EXPECT_EQ(*iter1, 1949);
    EXPECT_EQ(x[5], 1949);
    x[1] = 1;
    x[5] = 5;
  }

  // Increment
  {
    skip_iterator<int> iter = make_skip_iterator<int>(x.begin(), 0); // begin
    EXPECT_EQ(*(iter++), 1);
    EXPECT_EQ(*(iter++), 2);
    EXPECT_EQ(*(iter++), 3);
    EXPECT_EQ(*(iter++), 4);
    EXPECT_EQ(*(iter++), 5);
    EXPECT_EQ(*(iter++), 6);
    EXPECT_EQ(*(iter++), 7);
  }

  {
    skip_iterator<int> iter = make_skip_iterator<int>(x.begin(), 7); // begin
    EXPECT_EQ(*(iter++), 0);
    EXPECT_EQ(*(iter++), 1);
    EXPECT_EQ(*(iter++), 2);
    EXPECT_EQ(*(iter++), 3);
    EXPECT_EQ(*(iter++), 4);
    EXPECT_EQ(*(iter++), 5);
    EXPECT_EQ(*(iter++), 6);
  }

  {
    skip_iterator<int> iter = make_skip_iterator<int>(x.begin(), 3); // begin
    EXPECT_EQ(*(iter++), 0);
    EXPECT_EQ(*(iter++), 1);
    EXPECT_EQ(*(iter++), 2);
    EXPECT_EQ(*(iter++), 4);
    EXPECT_EQ(*(iter++), 5);
    EXPECT_EQ(*(iter++), 6);
    EXPECT_EQ(*(iter++), 7);
  }

  // distance
  {
    EXPECT_EQ(std::distance(x.begin(), x.end()), 8);

    skip_iterator<int> iter = make_skip_iterator<int>(x.begin(), 0); // begin
    skip_iterator<int> iter2 = make_skip_iterator<int>(x.end());
    EXPECT_EQ(std::distance(iter, iter2), 7);
  }

  {
    skip_iterator<int> iter = make_skip_iterator<int>(x.begin(), 7); // end
    skip_iterator<int> iter2 = make_skip_iterator<int>(x.end());
    EXPECT_EQ(std::distance(iter, iter2), 7);
  }

  {
    skip_iterator<int> iter = make_skip_iterator<int>(x.begin(), 5); // middle
    skip_iterator<int> iter2 = make_skip_iterator<int>(x.end());
    EXPECT_EQ(std::distance(iter, iter2), 7);
  }

  // pre/postfix
  {
    skip_iterator<int> iter = make_skip_iterator<int>(x.begin(), 1);
    EXPECT_EQ(*(iter), 0);
    EXPECT_EQ(*(++iter), 2);
    EXPECT_EQ(*(iter++), 2);
    EXPECT_EQ(*(iter++), 3);
  }
}
