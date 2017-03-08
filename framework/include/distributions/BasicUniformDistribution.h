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

#ifndef BASICUNIFORMDISTRIBUTION_H
#define BASICUNIFORMDISTRIBUTION_H

#include "Distribution.h"

class BasicUniformDistribution;

template<>
InputParameters validParams<BasicUniformDistribution>();

class BasicUniformDistribution : public Distribution
{
public:
  BasicUniformDistribution(const InputParameters & parameters);
  virtual ~BasicUniformDistribution(); 

protected:
  virtual Real pdf(Real x) override;
  virtual Real cdf(Real x) override;
  virtual Real inverseCdf(Real y) override;
  Real _lower_bound;
  Real _upper_bound;
};

#endif /* BASICUNIFORMDISTRIBUTION_H */
