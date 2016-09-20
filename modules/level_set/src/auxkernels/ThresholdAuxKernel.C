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

#include "ThresholdAuxKernel.h"

template<>
InputParameters validParams<ThresholdAuxKernel>()
{
  InputParameters params = validParams<AuxKernel>();
  params.addRequiredCoupledVar("threshold_variable", "The variable to compare the thresold value against");
  params.addParam<Real>("threshold", 0., "The value to compare the threshold variable against");
  params.addParam<Real>("above_value", 1., "The value to which the aux variable will be set");
  params.addParam<Real>("below_value", 0., "The value to which the aux variable will be set");

  return params;
}

ThresholdAuxKernel::ThresholdAuxKernel(const InputParameters & parameters) :
    AuxKernel(parameters),
    _threshold_variable(coupledValue("threshold_variable")),
    _threshold(getParam<Real>("threshold")),
    _above_value(getParam<Real>("above_value")),
    _below_value(getParam<Real>("below_value"))
{
  // _compare = &std::greater<Real>;
}

Real
ThresholdAuxKernel::computeValue()
{
  if (_threshold_variable[_qp] >= _threshold)
    return _above_value;
  else
    return _below_value;
}
