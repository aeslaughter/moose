//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#pragma once

#include "GeneralPostprocessor.h"

class TestTimePeriodTimestepSetup : public GeneralPostprocessor
{
public:
  static InputParameters validParams();
  TestTimePeriodTimestepSetup(const InputParameters & parameters);
  virtual void timestepSetup() override;
  virtual Real getValue() override;
  virtual void initialize() override {}
  virtual void execute() override {}

protected:
  Real _value = 0;
};
