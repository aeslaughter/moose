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
#include "ReporterState.h"
#include "libmesh/parallel_object.h"
#include "libmesh/auto_ptr.h"
#include <unordered_map>

class FEProblemBase;

class ReporterData : public Restartable, public libMesh::ParallelObject
{
public:
  ReporterData(FEProblemBase & fe_problem);

  template <typename T>
  T & getReporterValue(const ReporterName & state_name);

  template <typename T, template<typename> class S>
  T & getReporterValue(const ReporterName & state_name);

  void finalize(const std::string & object_name);

private:
  template <typename T, template<typename> class S>
  ReporterState<T> & getReporterStateHelper(const ReporterName & state_name);

  std::unordered_map<ReporterName, std::unique_ptr<ReporterStateBase>> _reporter_values;
};

template <typename T, template<typename> class S>
ReporterState<T> &
ReporterData::getReporterStateHelper(const ReporterName & state_name)
{
  auto state_pair = _reporter_values.find(state_name);
  if (state_pair == _reporter_values.end())
  {
    auto unique_ptr = libmesh_make_unique<S<T>>(declareRestartableDataWithObjectName<T>(
        state_name.getValueName(), state_name.getObjectName()));

    _reporter_values.emplace(state_name, std::move(unique_ptr));
    state_pair = _reporter_values.find(state_name);
  }

  auto & state = static_cast<ReporterState<T> &>(*(state_pair->second));
  return state;
}

template <typename T>
T &
ReporterData::getReporterValue(const ReporterName & state_name)
{
  const ReporterState<T> & state = getReporterStateHelper<T, ReporterState>(state_name);
  return state.getValue();
}

template <typename T, template<typename> class S>
T &
ReporterData::getReporterValue(const ReporterName & state_name)
{
  const ReporterState<T> & state = getReporterStateHelper<T, S>(state_name);
  return state.getValue();
}
