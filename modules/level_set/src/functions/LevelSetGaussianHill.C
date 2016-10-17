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

#include "LevelSetGaussianHill.h"

template<>
InputParameters validParams<LevelSetGaussianHill>()
{
  InputParameters params = validParams<Function>();
  params.addParam<Real>("sigma", 0.0625, "Standard deviation.");
  params.addParam<std::vector<Real> >("center", std::vector<Real>({0.5, 0.5, 0.0}), "Location of the hill centroid.");
  return params;
}

LevelSetGaussianHill::LevelSetGaussianHill(const InputParameters & parameters) :
  Function(parameters),
  _sigma(getParam<Real>("sigma")),
  _center(getParam<std::vector<Real> >("center"))
{
}

Real
LevelSetGaussianHill::value(Real /*t*/, const Point & p)
{
  RealVectorValue x_bar;

  for (unsigned int i = 0; i < _center.size(); ++i)
    x_bar(i) = p(i) - _center[i];

  return exp(- x_bar.size_sq() / (2*_sigma*_sigma));

}
