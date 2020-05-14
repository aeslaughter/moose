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

/**
 * Generic container for type independent Reporter values
 */
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
  T & currentValue() const;
  T & oldValue() const;

protected:
  T & _current;
  T & _old;
};

template <typename T>
ReporterState<T>::ReporterState(T & current, T & old)
  : ReporterStateBase, current(current), old(old)
{
}

template <typename T>
T &
ReporterState<T>::currentValue() const
{
  return _current;
}

template <typename T>
T &
ReporterState<T>::oldValue() const
{
  return _old;
}

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
