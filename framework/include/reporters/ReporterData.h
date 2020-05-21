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
#include "MooseApp.h"
#include "libmesh/parallel_object.h"
#include "libmesh/auto_ptr.h"
#include <unordered_map>

class FEProblemBase;

class ReporterData : public Restartable, public libMesh::ParallelObject
{
public:
  ReporterData(FEProblemBase & fe_problem);

  template <typename T>
  const T & getReporterValue(const ReporterName & state_name);

  template <typename T, template<typename> class S>
  T & declareReporterValue(const ReporterName & state_name);

  void finalize(const std::string & object_name);

private:
  //template <typename T, template<typename> class S>
   //ReporterState<T> & getReporterStateHelper(const ReporterName & state_name);

  std::unordered_map<ReporterName, std::unique_ptr<ReporterStateBase>> _reporter_states;
};

/*
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
*/

/*
template <typename T>
T &
ReporterData::getReporterValue(const ReporterName & state_name)
{
  const ReporterState<T> & state = getReporterStateHelper<T, ReporterState>(state_name);
  return state.getValue();
}
*/

template <typename T, template<typename> class S>
T &
ReporterData::declareReporterValue(const ReporterName & state_name)
{
  T & value = declareRestartableDataWithObjectName<T>(state_name.getValueName(),
                                                      state_name.getObjectName());

  auto unique_ptr = libmesh_make_unique<S<T>>(value);
  _reporter_states.emplace(state_name, std::move(unique_ptr));

  return value;
}





template <typename T>
const T &
ReporterData::getReporterValue(const ReporterName & state_name)
{
  _restartable_read_only = true;
  return declareRestartableDataWithObjectName<T>(state_name.getValueName(),
                                                 state_name.getObjectName());
  _restartable_read_only = false;

/*
  const std::string full_name(_restartable_system_name + "/" + state_name.getObjectName() + "/" + state_name.getValueName());
  const RestartableDataMap & data = _restartable_app.getRestartableData()[0];
  std::unordered_map<std::string, RestartableDataValuePair>::const_iterator iter = data.find(data_name);


  if (iter != data.end())
    return declareRestartableDataWithObjectName<T>(state_name.getValueName(),
                                                   state_name.getObjectName());


  else
  {
    auto value_ptr = dynamic_cast<RestartableData<T>*>(iter->second.value.get());
    if (!value_ptr)
      mooseError("Failed to retrieve Reporter data '", state_name.getValueName(),
                 "' from the object named '", state_name.getObjectName(),
                 "' for the desired type of '", typeid(T).name(),
                 "'; the desired data is of type '", iter->second.value->type(), "'.");
    return value_ptr->get();
  }
  */
}
