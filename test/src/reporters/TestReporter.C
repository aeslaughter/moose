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
    _string(declareValue<std::string>("string")),
    _bcast_value(declareValue<Real, ReporterBroadcastState>("broadcast"))
{
}

void
TestDeclareReporter::execute()
{
  _int = 1980;
  _real = 1.2345;
  _vector = {1, 1.1, 1.2};
  _string = "string";

  if (processor_id() == 0)
    _bcast_value = 42;
}

InputParameters
TestGetReporter::validParams()
{
  InputParameters params = GeneralReporter::validParams();
  params.addRequiredParam<ReporterName>("int_reporter", "'int' reporter name");
  params.addRequiredParam<ReporterName>("real_reporter", "'real' reporter name");
  params.addRequiredParam<ReporterName>("vector_reporter", "'vector' reporter name");
  params.addRequiredParam<ReporterName>("string_reporter", "'string' reporter name");
  params.addRequiredParam<ReporterName>("broadcast_reporter", "'broadcast' reporter name");
  return params;
}

TestGetReporter::TestGetReporter(const InputParameters & parameters)
  : GeneralReporter(parameters),
    _int(getReporterValue<int>("int_reporter")),
    _real(getReporterValue<Real>("real_reporter")),
    _vector(getReporterValue<std::vector<Real>>("vector_reporter")),
    _string(getReporterValue<std::string>("string_reporter")),
    _bcast_value(getReporterValue<Real, ReporterBroadcastState>("broadcast_reporter"))
{
}

void
TestGetReporter::execute()
{
  if (_int != 1980)
    mooseError("int reporter test failed");
  if (_real != 1.2345)
    mooseError("Real reporter test failed");
  if (_vector != std::vector<Real>({1., 1.1, 1.2}))
    mooseError("std::vector<Real> reporter test failed");
  if (_string != "string")
    mooseError("std::string reporter test failed");
  if (_bcast_value != 42)
    mooseError("Broadcast reporter test failed");
}
