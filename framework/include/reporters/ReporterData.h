//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#pragma once

#include "RestartableData.h"
#include "ReporterState.h"
#include "libmesh/parallel_object.h"
#include "libmesh/auto_ptr.h"
#include "MooseApp.h"
//class MooseApp;

/**
 * Data stored in MooseApp restartable data
 * Consolidates code and handles old/older/... data
 * Implements context class for customizable parallel stuff
 *
 * Data is not threaded, the calculation can be via UO, but the resulting data is not
 *
 */

class ReporterData
{
public:

  // The old/older values are stored in vector and this vector must have memory that doesn't
  // get reallocated. This is because the calls to getReporterValue can occur in any order using
  // any time index.
  constexpr static std::size_t HISTORY_CAPACITY = 5;

  ReporterData(MooseApp & moose_app);

  /*
  template <typename T>
  const T & getReporterValue(const ReporterName & reporter_name, const T & default_value);
  */

  template <typename T>
  const T & getReporterValue(const ReporterName & reporter_name, const std::size_t time_index = 0);

  template <typename T, template<typename> class S>
  T & declareReporterValue(const ReporterName & state_name);

  template <typename T, template<typename> class S>
  T & declareReporterValue(const ReporterName & state_name, const T & default_value);


  void initialize(const std::string & object_name);
  void finalize(const std::string & object_name);

  void init();
  void copyValuesBack();

private:

  MooseApp & _app;

  template <typename T>
  ReporterState<T> & getReporterStateHelper(const ReporterName & reporter_name, bool declare);


  //template <typename T, template<typename> class S>
   //ReporterState<T> & getReporterStateHelper(const ReporterName & state_name);

  // Convenience...
  std::set<RestartableDataValue *> _data_ptrs;

  std::set<std::unique_ptr<ReporterContextBase>> _context_ptrs;


  //std::unordered_map<ReporterName, std::unique_ptr<ReporterStateBase>> _reporter_states;

  bool _initialized = false;
};


template <typename T>
ReporterState<T> &
ReporterData::getReporterStateHelper(const ReporterName & reporter_name, bool declare)
{
  //
  if (_initialized)
    mooseError("An attempt was made to declare or get Reporter data with the name '", reporter_name, "' after FEProblemBase::init(), calls to get or declare Reporter data cannot be made after FEProblem::init(); all calls should be made in the object constructor.");

  const std::string data_name = "ReporterData/" + reporter_name.getObjectName() + "/" + reporter_name.getValueName();
  auto data_ptr = libmesh_make_unique<ReporterState<T>>(data_name);
  data_ptr->get().second.resize(ReporterData::HISTORY_CAPACITY);
  RestartableDataValue & value =
      _app.registerRestartableData(data_name, std::move(data_ptr), 0, !declare);
  auto & data_ref = static_cast<ReporterState<T>&>(value);
  _data_ptrs.insert(&data_ref);
  return data_ref;
}


template <typename T>
const T &
ReporterData::getReporterValue(const ReporterName & reporter_name, const std::size_t time_index)
{
  ReporterState<T> & data_ref = getReporterStateHelper<T>(reporter_name, false);
  return data_ref.value(time_index);
}

/*
template <typename T>
const T &
ReporterData::getReporterValue(const ReporterName & reporter_name, const T & default_value)
{
  ReporterState<T> & data_ref = getReporterStateHelper<T>(reporter_name, false);
  data_ref.get().first = default_value;
  return data_ref.value();
}
*/

template <typename T, template<typename> class S>
T &
ReporterData::declareReporterValue(const ReporterName & reporter_name)
{
  ReporterState<T> & data_ref = getReporterStateHelper<T>(reporter_name, true);

  if (data_ref.context() == nullptr)
  {
    auto context_ptr = libmesh_make_unique<S<T>>(data_ref);
    auto emplace_pair = _context_ptrs.emplace(std::move(context_ptr));
    data_ref.setContext(emplace_pair.first->get());
  }

  return data_ref.value();
}


template <typename T, template<typename> class S>
T &
ReporterData::declareReporterValue(const ReporterName & reporter_name, const T & default_value)
{
  ReporterState<T> & data_ref = getReporterStateHelper<T>(reporter_name, true);

  if (data_ref.context() == nullptr)
  {
    auto context_ptr = libmesh_make_unique<S<T>>(data_ref);
    auto emplace_pair = _context_ptrs.emplace(std::move(context_ptr));
    data_ref.setContext(emplace_pair.first->get());
  }

  data_ref.get().first = default_value;
  return data_ref.value();
}



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
/*
// TODO: add optional initial value overload
template <typename T, template<typename> class S>
T &
ReporterData::declareReporterValue(const ReporterName & state_name)
{
  if (_initialized)
    mooseError("The Reporter...");



  T & value = declareRestartableDataWithObjectName<T>(state_name.getValueName(),
                                                      state_name.getObjectName());

  auto unique_ptr = libmesh_make_unique<S<T>>(value);
  _reporter_states.emplace(state_name, std::move(unique_ptr));

  return value;
}
*/



/*
template <typename T>
const T &
ReporterData::getReporterValue(const ReporterName & state_name)
{
  _restartable_read_only = true;
  const T & value = declareRestartableDataWithObjectName<T>(state_name.getValueName(),
                                                            state_name.getObjectName());
  _restartable_read_only = false;



  return value;
*/
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
//}
