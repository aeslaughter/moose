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

#ifndef RANDOMGENERATOR_H
#define RANDOMGENERATOR_H

#include "MooseTypes.h"

class MersenneTwister;

class RandomGenerator
{
public:
  RandomGenerator();
  virtual ~RandomGenerator();
  virtual void seed(unsigned int seed);
  Real random();
protected:  
  MersenneTwister * _rng;
  const Real _range;
};


#endif /* RANDOMGENERATOR_H */

