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

#include "LevelSetForcingFunctionSUPG.h"

template<>
InputParameters validParams<LevelSetForcingFunctionSUPG>()
{
  InputParameters params = validParams<UserForcingFunction>();
  params.addClassDescription("The SUPG stablization term for a forcing function.");
  params += validParams<LevelSetVelocityInterface<> >();
  return params;
}

LevelSetForcingFunctionSUPG::LevelSetForcingFunctionSUPG(const InputParameters & parameters) :
    LevelSetVelocityInterface<UserForcingFunction>(parameters)
{
}

Real
LevelSetForcingFunctionSUPG::computeQpResidual()
{
  computeQpVelocity();
  Real tau = _current_elem->hmin() / (2 * _velocity.norm());
  return -tau * _velocity * _grad_test[_i][_qp] * f();
}

Real
LevelSetForcingFunctionSUPG::computeQpJacobian()
{
  computeQpVelocity();
  Real tau = _current_elem->hmin() / (2 * _velocity.norm());
  return -tau * _velocity * _grad_test[_i][_qp] * f();
}
