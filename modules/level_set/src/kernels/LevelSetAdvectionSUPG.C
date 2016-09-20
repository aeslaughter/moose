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

#include "LevelSetAdvectionSUPG.h"

template<>
InputParameters validParams<LevelSetAdvectionSUPG>()
{
  InputParameters params = validParams<Kernel>();
  params += validParams<LevelSetVelocityInterface<> >();
  return params;
}

LevelSetAdvectionSUPG::LevelSetAdvectionSUPG(const InputParameters & parameters) :
    LevelSetVelocityInterface<Kernel>(parameters)
{
}

Real
LevelSetAdvectionSUPG::computeQpResidual()
{
  computeQpVelocity();
  Real tau = _current_elem->hmax() / (2 * _velocity.size());
  return tau * _velocity * _grad_test[_i][_qp] * _velocity * _grad_u[_qp];
}

Real
LevelSetAdvectionSUPG::computeQpJacobian()
{
  computeQpVelocity();
  Real tau = _current_elem->hmax() / (2 * _velocity.size());
  return tau * _velocity * _grad_test[_i][_qp] * _velocity * _grad_phi[_j][_qp];
}
