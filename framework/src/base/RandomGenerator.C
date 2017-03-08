/****************************************************************/
/*               DO NOT MODIFY THIS HEADER                      */
/* MOOSE - Multiphysics Object Oriented Simulation Environment  */
/*                                                              */
/*           (c) 2010 Battelle Energy Alliance, LLC             */
/*                   ALL RIGHTS RESERVED                        */
/*                                                              */
/*          Prepared by Battelle Energy Alliance, LLC           */
/*            Under Contract No. DE-AC07-05ID14517              */
/*            With the U. S. Department of Energy               */
/*                                                              */
/*            See COPYRIGHT for full restrictions               */
/****************************************************************/

#include "RandomGenerator.h"
#include  <random>

class MersenneTwister
{
public:
  std::mt19937 _mt_eng;
};

RandomGenerator::RandomGenerator()
  : _rng(new MersenneTwister()),
    _range(_rng->_mt_eng.max() - _rng->_mt_eng.min())
{
}

RandomGenerator::~RandomGenerator()
{
  delete _rng;
}

void RandomGenerator::seed(unsigned int seed)
{
  _rng->_mt_eng.seed(seed);
}

Real
RandomGenerator::random()
{
  return (_rng->_mt_eng() - _rng->_mt_eng.min())/_range;
}

