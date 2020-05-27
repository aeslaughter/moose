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
#include "RestartableData.h"

template <typename T>
class ReporterState : public RestartableData<std::pair<T, std::vector<T>>>
{
public:
  ReporterState(std::string name) : RestartableData<std::pair<T, std::vector<T>>>(name, nullptr)
    {
    }

  T & value(const std::size_t time_index = 0);

  void init();
  void copyValuesBack();


  void setContext(void * void_ptr)
    {
      this->_context = void_ptr;
    }



private:
  std::size_t _max_requested_time_index = 0;


};


template <typename T>
T &
ReporterState<T>::value(const std::size_t time_index)
{
  _max_requested_time_index = std::max(_max_requested_time_index, time_index);
  if (time_index == 0)
    return this->get().first;
  else
  {
    mooseAssert(time_index - 1 < this->get().second.size(), "The desired time index " << time_index << " is out of range of the size of " << this->get().second.size());
    return this->get().second[time_index - 1];
  }

}

template <typename T>
void
ReporterState<T>::init()
{
  T & value = this->get().first;
  std::vector<T> & old_values = this->get().second;

  old_values.resize(_max_requested_time_index);

  for (std::size_t i = 0; i < old_values.size(); ++i)
    old_values[i] = value;
}

template <typename T>
void
ReporterState<T>::copyValuesBack()
{
  T & value = this->get().first;
  std::vector<T> & old_values = this->get().second;

  for (std::size_t i = 1; i < old_values.size(); ++i)
    old_values[i] = old_values[i-1];

  if (old_values.size() > 0)
    old_values[0] = value;
}


class ReporterContextBase
{
public:
  ReporterContextBase() = default;
  virtual ~ReporterContextBase() = default;
  virtual void init() = 0;
  virtual void copyValuesBack() = 0;
};

template <typename T>
class ReporterContext : public ReporterContextBase
{
public:
  ReporterContext(ReporterState<T> & state) : ReporterContextBase(),
                                                  _state(state)
    {
    }

  virtual void init() override;
  virtual void copyValuesBack() override;


protected:

  ReporterState<T> & _state;
};


template <typename T>
void
ReporterContext<T>::init()
{
  _state.init();
  /*
  for (std::size_t i = 0; i < _max_requested_time_index; ++i)
    this->get().second.push_back(this->get().first);
  this->get().second.shrink_to_fit();
  */
}


template <typename T>
void
ReporterContext<T>::copyValuesBack()
{
  _state.copyValuesBack();
}



//class ReporterStateBase
 //{
//public:
//  ReporterStateBase() = default;
//  virtual ~ReporterStateBase() = default;
//  // virtual void initialize(const libMesh::Parallel::Communicator * comm) {}d
//  virtual void finalize(const libMesh::Parallel::Communicator & /*comm*/)
//    {
//      std::cout << "ReporterStateBase::finalize" << std::endl;
//    }
//};
//
 //template <typename T>
 //class ReporterState : public ReporterStateBase
 //{
//public:
//  ReporterState(T & value);
//  T & getValue(const std::size_t time_index = 0) const;
//
//  //void initValue(const std::size_t time_index, T & value);
//
//  virtual void finalize(const libMesh::Parallel::Communicator & /*comm*/) override
//    {
//      std::cout << "ReporterState::finalize" << std::endl;
//    }
//
//protected:
//  std::vector<T*> _values;
//};

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
//  virtual void finalize(const libMesh::Parallel::Communicator & comm) override
//    {
//      std::cout << "ReporterBroadcastState::finalize" << std::endl;
//      //comm.broadcast(this->_values);
//    }
};
