//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#include "Counter.h"

#include "SubProblem.h"

registerMooseObject("MooseApp", Counter);

InputParameters
Counter::validParams()
{
  InputParameters params = GeneralReporter::validParams();
  return params;
}

Counter::Counter(const InputParameters & parameters) : GeneralReporter(parameters) {}

void
Counter::execute()
{
  std::cout << name() << std::endl;
  // return _subproblem.nLinearIterations();
}
