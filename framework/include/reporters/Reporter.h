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

class Reporter : public OutputInterface
{
public:
  static InputParameters validParams();
  Reporter(const InputParameters & parameters);
  virtual ~Reporter() = default;

protected:
  template <typename T>
  T & declareValue(const std::string & value_name);

private:
  const std::string & _reporter_name;

  const THREAD_ID _reporter_tid;

  FEProblemBase * _reporter_fe_problem;
};

template <typename T>
T &
Reporter::declareValue(const std::string & value_name)
{
  return _reporter_fe_problem->declareReporterValue<T>(_reporter_name, value_name);
}
