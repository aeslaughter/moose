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
#include "LevelSetAdvection.h"

template<>
InputParameters validParams<LevelSetAdvection>()
{
  InputParameters params = validParams<Kernel>();
  params.addClassDescription("Implements the level set advection equation: $\\vec{v}\\cdot\\nabla u = 0$, where the weak form is $(\\Psi_i, \\vec{v}\\cdot\\nabla u) = 0$.");
  params += validParams<LevelSetVelocityInterface<> >();
  return params;
}

LevelSetAdvection::LevelSetAdvection(const InputParameters & parameters) :
    LevelSetVelocityInterface<Kernel>(parameters)
{
}

Real
LevelSetAdvection::computeQpResidual()
{
  computeQpVelocity();
  return _test[_i][_qp] * (_velocity * _grad_u[_qp]);
}

Real
LevelSetAdvection::computeQpJacobian()
{
  computeQpVelocity();
  return _test[_i][_qp] * (_velocity * _grad_phi[_j][_qp]);
}
