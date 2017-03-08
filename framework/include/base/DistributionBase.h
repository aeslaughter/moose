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

#ifndef DISTRIBUTIONBASE_H
#define DISTRIBUTIONBASE_H

#include "RandomGenerator.h"
#include<string>

const unsigned int _default_seed = 1031092845; 

class DistributionBase
{
public:
  DistributionBase();
  virtual ~DistributionBase();

  virtual Real pdf(Real x) = 0;
  virtual Real cdf(Real x) = 0;
  virtual Real inverseCdf(Real y) = 0;
  /// random sample
  virtual Real random();
  /// Get distribution type
  std::string & getType();
  unsigned int getSeed();
  virtual void setSeed(unsigned int seed);

///protected:
  RandomGenerator * _random;
  std::string _dist_type;
  unsigned int _seed;
};

#endif /* DISTRIBUTIONBASE_H*/
