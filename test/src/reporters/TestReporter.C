//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#include "TestReporter.h"

registerMooseObject("MooseTestApp", TestDeclareReporter);
registerMooseObject("MooseTestApp", TestGetReporter);

InputParameters
TestDeclareReporter::validParams()
{
  InputParameters params = GeneralReporter::validParams();
  return params;
}

TestDeclareReporter::TestDeclareReporter(const InputParameters & parameters)
  : GeneralReporter(parameters),
    _int(declareValue<int>("int")),
    _real(declareValue<Real>("real")),
    _vector(declareValue<std::vector<Real>>("vector")),
    _string(declareValue<std::string>("string"))
{
}

void
TestDeclareReporter::execute()
{
  _int = 1980;
  _real = 1.2345;
  _vector = {1, 1.1, 1.2};
}

void
TestDeclareReporter::finalize()
{
}

InputParameters
TestGetReporter::validParams()
{
  InputParameters params = GeneralReporter::validParams();
  params.addRequiredParam<ReporterName>("int_reporter", "'int' reporter name");
  return params;
}

TestGetReporter::TestGetReporter(const InputParameters & parameters)
  : GeneralReporter(parameters), _int(getReporterValue<int>("int_reporter"))
{
}

void
TestGetReporter::execute()
{
  if (_int != 1980)
    mooseError("int reporter test failed");
}

void
TestGetReporter::finalize()
{
}
