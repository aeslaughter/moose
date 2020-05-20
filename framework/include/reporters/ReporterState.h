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
#include <iostream>

class ReporterStateBase
{
public:
  ReporterStateBase() = default;
  virtual ~ReporterStateBase() = default;
  virtual void initialize(const libMesh::Parallel::Communicator * comm) {}
  virtual void finalize(const libMesh::Parallel::Communicator * comm) {}
};

template <typename T>
class ReporterState : public ReporterStateBase
{
public:
  ReporterState(T & current);
  T & getValue() const;
  // T & getOldValue() const;

protected:
  T & _value;
  // T & _value_old;
};

template <typename T>
ReporterState<T>::ReporterState(T & value) //, T & value_old)
  : ReporterStateBase(), _value(value)     //, _value_old(value_old)
{
}

template <typename T>
T &
ReporterState<T>::getValue() const
{
  return _value;
}

// DEMO FOR ADDING PARALLEL TYPES
/*
template <typename>
class BroadcastReporterState : public ReporterState
{
public:
  BroadcastReporterState(T & current, const libMesh::Parallel::Communicator * comm);
  virtual void finalize() override;

protected:
  const libmesh::Parallel::Communicator * _comm;
};

template <typename T>
T &
BroadcastReporterState(T & current, const libMesh::Parallel::Communicator * comm) :
    ReporterState<T>(current),
    _comm(comm)
{
}

template <typename T>
void
BroadcastReporterState<T>::finalize()
{
  std::cout << "here................." << std::endl;
}


using BroadcastReal = Real;
*/

class ReporterStateName
{
public:
  ReporterStateName(const std::string & object_name, const std::string & value_name);
  ReporterStateName(const ReporterStateName & other);
  ReporterStateName & operator=(const ReporterStateName & other);

  ReporterStateName() {}
  // friend class InputParameters;

  const std::string & getObjectName() const;
  const std::string & getValueName() const;

  operator std::string() const;
  bool operator==(const ReporterStateName & rhs) const;

private:
  std::string _object_name;
  std::string _value_name;
  std::string _combined_name;
};

template <>
struct std::hash<ReporterStateName>
{
  std::size_t operator()(const ReporterStateName & other) const
  {
    return std::hash<std::string>{}(other);
  }
};

std::ostream & operator<<(std::ostream & os, const ReporterStateName & state);
