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
#include "LevelSetSussmanReinitialization.h"

template<>
InputParameters validParams<LevelSetSussmanReinitialization>()
{
  InputParameters params = validParams<Diffusion>();
  params.addRequiredParam<PostprocessorName>("epsilon", "The epsilon coefficient to be used in the reinitialization calculation.");
  return params;
}

LevelSetSussmanReinitialization::LevelSetSussmanReinitialization(const InputParameters & parameters) :
    Diffusion(parameters),
    _epsilon(getPostprocessorValue("epsilon"))
    {
}

Real
LevelSetSussmanReinitialization::computeQpResidual()
{
  return _test[_i][_qp] * sign() * (_grad_u[_qp].size() - 1);
}

Real
LevelSetSussmanReinitialization::computeQpJacobian()
{
  return 0.0;
}

Real
LevelSetSussmanReinitialization::sign()
{
  return _u[_qp] / std::sqrt(_u[_qp]*_u[_qp] + _epsilon*_epsilon);
}

Real
LevelSetSussmanReinitialization::dsign()
{
  return 0.0;
}
