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
  virtual void finalize(const libMesh::Parallel::Communicator & /*comm*/)
    {
      std::cout << "ReporterStateBase::finalize" << std::endl;
    }
};

template <typename T>
class ReporterState : public ReporterStateBase
{
public:
  ReporterState(T & value);
  T & getValue(const std::size_t time_index = 0) const;

  //void initValue(const std::size_t time_index, T & value);

  virtual void finalize(const libMesh::Parallel::Communicator & /*comm*/) override
    {
      std::cout << "ReporterState::finalize" << std::endl;
    }

protected:
  std::vector<T*> _values;
};

/*
template <typename T>
void
ReporterState::initValue(const std::size_t time_index, T & value)
{
*/




template <typename T>
class ReporterBroadcastState : public ReporterState<T>
{
public:
  ReporterBroadcastState(T & value);
  virtual void finalize(const libMesh::Parallel::Communicator & comm) override
    {
      std::cout << "ReporterBroadcastState::finalize" << std::endl;
      //comm.broadcast(this->_values);
    }
};
