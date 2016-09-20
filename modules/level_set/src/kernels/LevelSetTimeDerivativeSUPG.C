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

#include "LevelSetTimeDerivativeSUPG.h"

template<>
InputParameters validParams<LevelSetTimeDerivativeSUPG>()
{
  InputParameters params = validParams<TimeDerivative>();
  params += validParams<LevelSetVelocityInterface<> >();
  return params;
}

LevelSetTimeDerivativeSUPG::LevelSetTimeDerivativeSUPG(const InputParameters & parameters) :
    LevelSetVelocityInterface<TimeDerivative>(parameters)
{
}

Real
LevelSetTimeDerivativeSUPG::computeQpResidual()
{
  computeQpVelocity();
  Real tau = _current_elem->hmax() / (2 * _velocity.size());
  return tau * _velocity * _grad_test[_i][_qp] * _u_dot[_qp];
}

Real
LevelSetTimeDerivativeSUPG::computeQpJacobian()
{
  computeQpVelocity();
  Real tau = _current_elem->hmax() / (2 * _velocity.size());
  return tau * _velocity * _grad_test[_i][_qp] * _du_dot_du[_qp];
}
