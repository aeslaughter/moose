//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#include "TestReporter.h"

#include "SubProblem.h"

registerMooseObject("MooseTestApp", TestReporter);

InputParameters
TestReporter::validParams()
{
  InputParameters params = GeneralReporter::validParams();
  MooseEnum num("elements nodes");
  params.addParam<MooseEnum>("count", num, "The number to count.");
  params.addRequiredParam<ReporterName>("reporter", "The name of the reporter to get.");
  return params;
}

TestReporter::TestReporter(const InputParameters & parameters)
  : GeneralReporter(parameters) /*, _declare_value(declareValue<Real>("declare")),
                                  _get_value(getReporterValue<Real>("name"))*/
{
  std::cout << getParam<ReporterName>("reporter") << std::endl;
}

void
TestReporter::execute()
{
  //  _declare_value = _mesh.n_elem();
}

void
TestReporter::finalize()
{
}
