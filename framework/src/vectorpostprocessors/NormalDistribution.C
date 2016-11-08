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

// MOOSE includes
#include "NormalDistribution.h"

template<>
InputParameters validParams<NormalDistribution>()
{
  InputParameters params = validParams<GeneralVectorPostprocessor>();
  params.addRequiredParam<Real>("standard_deviation", "The standard deviation of the normal distribution.");
  params.addRequiredParam<Real>("mean", "The mean of the normal distribution.");
  params.addRequiredParam<unsigned int>("count", "The number of random points to sample.");
  return params;
}


NormalDistribution::NormalDistribution(const InputParameters & parameters) :
    GeneralVectorPostprocessor(parameters),
    _value(declareVector("distribution")),
    _standard_deviation(getParam<Real>("standard_deviation")),
    _mean(getParam<Real>("mean")),
    _count(getParam<unsigned int>("count")),
    _distribution(_mean, _standard_deviation),
    _generator(_random_device())
{
}

void
NormalDistribution::initialize()
{
  _value.resize(_count);
}

void
NormalDistribution::execute()
{
  for (unsigned int i = 0; i < _count; ++i)
    _value[i] = sample();
}


Real
NormalDistribution::sample()
{
  return _distribution(_generator);
}
