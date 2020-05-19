//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html
#pragma once

class ReporterInterface
{
public:
  ReporterInterface(const MooseObject * moose_object);

  /*
  template <typename T>
  const T & getReporterValue(const ReporterName & name);

  template <typename T>
  const T & getReporterValueByName(const std::string & object_name, const std::string & value_name);
  */

private:
  const InputParameters & _ri_params;
  FEProblemBase & _ri_fe_problem_base;
};

/*
template <typename T>
const T &
ReporterInterface::getReporterValueByName(const std::string & object_name, const std::string &
value_name)
{
  return _ri_fe_problem_base.getReporterValue<T>(object_name, value_name);
}

template <typename T>
const T &
ReporterInterface::getReporterValue(const ReporterName & name)
{
  const ReporterName & reporter_name,
  return _ri_fe_problem_base.getReporterValue<T>(object_name, value_name);
}
*/
