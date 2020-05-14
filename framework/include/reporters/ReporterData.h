//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#pragma once

#include "Restartable.h"
#include "libmesh/parallel_object.h"
#include <unordered_map>

class FEProblemBase;

class ReporterData : public Restartable, public libMesh::ParallelObject
{
public:
  static InputParameters validParams();

  template <typename T>
  T & declareReporterValue(const std::string & object_name, const std::string & value_name);

  template <typename T>
  const T & getReporterValue(const std::string & object_name, const std::string & value_name);

private:
  template <typename T>
  ReporterState<T> & getReporterStateHelper(const std::string & object_name,
                                            const std::string & value_name);

  std::unordered_map<std::vector<std::unique_ptr<ReporterStateBase>>> _reporters;
};
