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

#include "DistributionBase.h"
#include "RandomGenerator.h"

DistributionBase::DistributionBase()
  : _random(new RandomGenerator()),
    _dist_type("UniformDistribution"),
    _seed(_default_seed)
{
}

DistributionBase::~DistributionBase()
{
  delete _random;
}

Real
DistributionBase::random()
{
  return inverseCdf(_random->random());
}

std::string &
DistributionBase::getType()
{
  return _dist_type;
}

unsigned int
DistributionBase::getSeed()
{
  return _seed;
}

void
DistributionBase::setSeed(unsigned int seed)
{
  _random->seed(seed);
}

