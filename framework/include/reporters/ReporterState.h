//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html
#pragma once

#include <iostream>
#include "libmesh/parallel.h"
#include "ReporterName.h"

class ReporterStateBase
{
public:
  ReporterStateBase() = default;
  virtual ~ReporterStateBase() = default;
  // virtual void initialize(const libMesh::Parallel::Communicator * comm) {}d
  virtual void finalize(const libMesh::Parallel::Communicator & /*comm*/) = 0;
};

template <typename T>
class ReporterState : public ReporterStateBase
{
public:
  ReporterState(T & current);
  T & getValue() const;
  // T & getOldValue() const;

  virtual void finalize(const libMesh::Parallel::Communicator & /*comm*/) override
  {
    std::cout << "ReporterState::finalize" << std::endl;
  }

protected:
  T & _value;
  // T & _value_old;
};




/*
template <template<typename> class U, typename T>
class ContainerReporterState : public ReporterStateBase
{
public:
  ContainerReporterState(U<T> & current);
  U<T> & getValue() const;
  // T & getOldValue() const;

  virtual void finalize(const libMesh::Parallel::Communicator & comm) final
  {
    std::cout << "ContainerReporterState::finalize" << std::endl;
  }

protected:
  U<T> & _value;
  // T & _value_old;
};
*/



// DEMO FOR ADDING PARALLEL TYPES
template <typename T>
class BroadcastValue
{
public:

  operator T() const { return _value; }
  BroadcastValue & operator=(const T & other)
    {
      _value = other;
      return *this;
    }
  T _value;
};




template <>
void
ReporterState<BroadcastValue<Real>>::finalize(const libMesh::Parallel::Communicator & /* comm*/);
