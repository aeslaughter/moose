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
#include "VectorReceiver.h"

template<>
InputParameters validParams<VectorReceiver>()
{
  InputParameters params = validParams<GeneralVectorPostprocessor>();
  params.addRequiredParam<Real>("default", "The default value to populate the vector postprocessor with.");
  params.addRequiredParam<unsigned int>("count", "The length of the vector.");
  return params;
}


VectorReceiver::VectorReceiver(const InputParameters & parameters) :
    GeneralVectorPostprocessor(parameters),
    _value(declareVector("vector")),
    _default(getParam<Real>("default")),
    _count(getParam<unsigned int>("count"))
{
}

void
VectorReceiver::initialSetup()
{
  _value.resize(_count);
  for (unsigned int i = 0; i < _count; ++i)
    _value[i] = _default;
}
