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
#include "LevelSetOlssonReinitialization.h"

template<>
InputParameters validParams<LevelSetOlssonReinitialization>()
{
  InputParameters params = validParams<Diffusion>();
  params.addRequiredCoupledVar("phi_0", "The level set variable to be reinitialized as sign distance function.");
  params.addRequiredParam<Real>("epsilon", "The epsilon coefficient to be used in the reinitialization calculation.");
  return params;
}

LevelSetOlssonReinitialization::LevelSetOlssonReinitialization(const InputParameters & parameters) :
    Diffusion(parameters),
    _grad_levelset_0(coupledGradient("phi_0")),
    _epsilon(getParam<Real>("epsilon"))
{
}

Real
LevelSetOlssonReinitialization::computeQpResidual()
{
  _s = _grad_levelset_0[_qp].norm() + std::numeric_limits<Real>::epsilon();
  _n_hat = _grad_levelset_0[_qp] / _s;
  _f = _u[_qp] * ( 1 - _u[_qp]) * _n_hat;
//  Real epsilon = _current_elem->hmin();
  return _grad_test[_i][_qp] * (-_f + _epsilon*(_grad_u[_qp]*_n_hat)*_n_hat );
}

Real
LevelSetOlssonReinitialization::computeQpJacobian()
{
  _s = _grad_levelset_0[_qp].norm() + std::numeric_limits<Real>::epsilon();
  _n_hat = _grad_levelset_0[_qp] / _s;
  //Real epsilon = _current_elem->hmin();
  return _grad_test[_i][_qp] * _n_hat * ((2*_u[_qp]-1)*_phi[_j][_qp] + _epsilon*(_grad_phi[_j][_qp]*_n_hat));
}

Real
LevelSetOlssonReinitialization::computeQpOffDiagJacobian(const unsigned int jvar)
{
  return 0.0;
}
