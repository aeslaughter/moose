//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#pragma once

#include "OutputInterface.h"
#include "FEProblemBase.h"
//#include "ReporterState.h"

class Reporter : public OutputInterface
{
public:
  static InputParameters validParams();
  Reporter(const InputParameters & parameters);
  virtual ~Reporter() = default;

protected:
  template <typename T, template<typename> class S=ReporterContext>
  T & declareValue(const std::string & value_name);

  template <typename T, template<typename> class S=ReporterContext>
  T & declareValue(const std::string & value_name, const T & default_value);

private:
  const std::string & _reporter_name;

  FEProblemBase * _reporter_fe_problem;
};

template <typename T, template<typename> class S>
T &
Reporter::declareValue(const std::string & value_name)
{
  ReporterName state_name(_reporter_name, value_name);
  return _reporter_fe_problem->getReporterData().declareReporterValue<T, S>(state_name);
}


template <typename T, template<typename> class S>
T &
Reporter::declareValue(const std::string & value_name, const T & default_value)
{
  ReporterName state_name(_reporter_name, value_name);
  return _reporter_fe_problem->getReporterData().declareReporterValue<T, S>(state_name, default_value);
}
