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

#include "LevelSetValueMarker.h"

template<>
InputParameters validParams<LevelSetValueMarker>()
{
  InputParameters params = validParams<ValueRangeMarker>();
  params += validParams<LevelSetVelocityInterface<> >();
  params.addParam<Real>("bound_scale", 1.5, "The scale to apply to the bounds in the direction of the velocity front.");
  return params;
}

LevelSetValueMarker::LevelSetValueMarker(const InputParameters & parameters) :
  LevelSetVelocityInterface<ValueRangeMarker>(parameters),
    _input_upper_bound(getParam<Real>("upper_bound")),
    _input_lower_bound(getParam<Real>("lower_bound")),
    _bound_scale(getParam<Real>("bound_scale")),
    _grad_levelset_var(coupledGradient("variable"))
{
}

Marker::MarkerValue
LevelSetValueMarker::computeQpMarker()
{
  // Compute the levelset variable normal direction
  _n_hat = _grad_levelset_var[_qp] / _grad_levelset_var[_qp].size();

  // Dot the normal with the velocity
  computeQpVelocity();
  _v_dot_n = _n_hat * _velocity;

  // Determine if we are inside the levelset range
  _inside = _u[_qp] < 0;

  // Reset the upper and lower bounds used by ValueRangeMarker::computeQpMarker
  _lower_bound = _input_lower_bound;
  _upper_bound = _input_upper_bound;

  // Adjust the upper/lower values based on the velocity
  if (_v_dot_n > 0 && !_inside)
    _upper_bound *=  _bound_scale;

  else if (_v_dot_n < 0 && _inside)
    _lower_bound *= _bound_scale;

  // Compte the marker using the base class
  return ValueRangeMarker::computeQpMarker();
}
