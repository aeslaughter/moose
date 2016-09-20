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

Real
LevelSetAdvection::computeQpOffDiagJacobian(const unsigned int jvar)
{
  /*
  if (jvar == _x_vel_var)
    return _test[_i][_qp] * _grad_u[_qp](0);
  else if (jvar == _y_vel_var)
    return _test[_i][_qp] * _grad_u[_qp](1);
  else if (jvar == _z_vel_var)
    return _test[_i][_qp] * _grad_u[_qp](2);
  else
  */
    return 0.0;
}
