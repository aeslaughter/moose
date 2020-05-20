//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html
#pragma once
#include "MooseTypes.h"
#include "InputParameters.h"
#include "FEProblemBase.h"

class ReporterInterface
{
public:
  static InputParameters validParams();

  ReporterInterface(const MooseObject * moose_object);

  template <typename T>
  const T & getReporterValue(const std::string & param_name) const;

  template <typename T>
  const T & getReporterValueByName(const ReporterName & state_name) const;

private:
  const InputParameters & _ri_params;
  FEProblemBase & _ri_fe_problem_base;
};

template <typename T>
const T &
ReporterInterface::getReporterValue(const std::string & param_name) const
{
  const ReporterName & rname = _ri_params.template get<ReporterName>(param_name);
  return getReporterValueByName<T>(rname);
}

template <typename T>
const T &
ReporterInterface::getReporterValueByName(const ReporterName & state_name) const
{
  return _ri_fe_problem_base.getReporterValue<T>(state_name);
}
