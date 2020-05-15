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

class ReporterStateBase
{
public:
  ReporterStateBase() = default;
  virtual ~ReporterStateBase() = default;
};

template <typename T>
class ReporterState : public ReporterStateBase
{
public:
  ReporterState(T & current, T & old);
  T & getValue() const;
  T & getOldValue() const;

protected:
  T & _value;
  T & _value_old;
};

template <typename T>
ReporterState<T>::ReporterState(T & value, T & value_old)
  : ReporterStateBase(), _value(value), _value_old(value_old)
{
}

template <typename T>
T &
ReporterState<T>::getValue() const
{
  return _value;
}

template <typename T>
T &
ReporterState<T>::getOldValue() const
{
  return _value_old;
}

class ReporterStateName
{
public:
  ReporterStateName(const std::string & object_name, const std::string & value_name);

  operator std::string() const;
  bool operator==(const ReporterStateName & rhs) const;

private:
  const std::string _combined_name;
};

template <>
struct std::hash<ReporterStateName>
{
  std::size_t operator()(const ReporterStateName & other) const
  {
    return std::hash<std::string>{}(other);
  }
};

/*
class ReporterStorage
{
public:
  ///@{
  // Default constructors
  ReporterStorage(){};
  ReporterStorage(const ReporterStorage &) = delete;
  ReporterStorage(ReporterStorage &&) = delete;
  ReporterStorage & operator=(const ReporterStorage &) = delete;
  ReporterStorage & operator=(ReporterStorage &&) = delete;
  ///@}

  std::vector<std::unique_ptr<ReporterStateBase>> _reporters;
};
*/
