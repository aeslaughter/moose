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

#include "Distribution.h"

template<>
InputParameters validParams<Distribution>()
{
  InputParameters params = validParams<MooseObject>();
  params.addParam<unsigned int>("seed", _default_seed, "Random number generator seed");
  params.addRequiredParam<std::string>("type", "Distribution type");
  params.registerBase("Distribution");
  params.declareControllable("enable");
  return params;
}

Distribution::Distribution(const InputParameters & parameters)
 : MooseObject(parameters),
   SetupInterface(this)
{
  _dist_type = getParam<std::string>("type");
  _seed = getParam<unsigned int>("seed");
  setSeed(_seed);
}

Distribution::~Distribution()
{
}

