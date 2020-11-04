//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#include "TestTimePeriodTimestepSetup.h"

registerMooseObject("MooseTestApp", TestTimePeriodTimestepSetup);

InputParameters
TestTimePeriodTimestepSetup::validParams()
{
  InputParameters params = GeneralPostprocessor::validParams();
  return params;
}

TestTimePeriodTimestepSetup::TestTimePeriodTimestepSetup(const InputParameters & parameters)
  : GeneralPostprocessor(parameters)
{
}

void
TestTimePeriodTimestepSetup::timestepSetup()
{
  _value = _t;
}

Real
TestTimePeriodTimestepSetup::getValue()
{
  return _value;
}
