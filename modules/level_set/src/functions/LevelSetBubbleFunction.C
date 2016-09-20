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
#include "LevelSetBubbleFunction.h"

template<>
InputParameters
validParams<LevelSetBubbleFunction>()
{
  InputParameters params = validParams<Function>();
  params.addParam<RealVectorValue>("center", RealVectorValue(0.5, 0.5, 0), "The center of the bubble.");
  params.addParam<Real>("radius", 0.15, "The radius of the bubble.");
  params.addParam<Real>("epsilon", 0.01, "The interface thickness.");
  return params;
}

LevelSetBubbleFunction::LevelSetBubbleFunction(const InputParameters & parameters):
    Function(parameters),
    _center(getParam<RealVectorValue>("center")),
    _radius(getParam<Real>("radius")),
    _epsilon(getParam<Real>("epsilon"))
{
}

Real
LevelSetBubbleFunction::value(Real /*t*/, const Point & p)
{
  Real x = ((p - _center).size() - _radius) / _epsilon;
  return 1.0 / (1 + exp(x));
}

RealGradient
LevelSetBubbleFunction::gradient(Real /*t*/, const Point & p)
{
  Real norm = (p - _center).size();
  Real g = (norm - _radius) / _epsilon;
  RealGradient output;

  Real g_prime;
  for (unsigned int i = 0; i < LIBMESH_DIM; ++i)
  {
    g_prime = (p(i) - _center(i)) / (_epsilon * norm);
    output(i) = (g_prime * exp(g)) / ((exp(g) + 1) * (exp(g) + 1));
  }
  return output;
}
