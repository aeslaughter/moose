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

// auto hash = [](const ReporterStateName & name){ return
// std::hash<std::string>{}(name.getCombinedName()); }; auto comp = [](const ReporterStateName & l,
// const ReporterStateName &r){ return l.getCombinedName() == r.getCombinedName(); };

class ReporterData : public Restartable, public libMesh::ParallelObject
{
public:
  ReporterData(FEProblemBase & fe_problem);

  template <typename T>
  T & getReporterValue(const ReporterStateName & state_name);

private:
  template <typename T>
  ReporterState<T> & getReporterStateHelper(const ReporterStateName & state_name);

  std::unordered_map<ReporterStateName, std::unique_ptr<ReporterStateBase>> _reporter_values;
};

template <typename T>
ReporterState<T> &
ReporterData::getReporterStateHelper(const ReporterStateName & state_name)
{
  auto state_pair = _reporter_values.find(state_name);
  if (state_pair == _reporter_values.end())
  {
    auto unique_ptr = libmesh_make_unique<ReporterState<T>>(declareRestartableDataWithObjectName<T>(
        state_name.getValueName(), state_name.getObjectName()));

    _reporter_values.emplace(state_name, std::move(unique_ptr));
    state_pair = _reporter_values.find(state_name);
  }
  /*
  auto state_pair = _reporter_values.emplace(
    std::piecewise_construct, std::forward_as_tuple(state_name),
    std::forward_as_tuple<ReporterState<T>>(declareRestartableDataWithObjectName<T>(state_name,
  "value"), declareRestartableDataWithObjectName<T>(state_name, "value_old")));
  */
  auto & state = static_cast<ReporterState<T> &>(*(state_pair->second));
  return state;
}

template <typename T>
T &
ReporterData::getReporterValue(const ReporterStateName & state_name)
{
  const ReporterState<T> & state = getReporterStateHelper<T>(state_name);
  return state.getValue();
}
