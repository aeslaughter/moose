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
 * Generic container for type independent VectorPostprocessor vector state
 */
class VectorPostprocessorVectorStateBase
{
public:
  VectorPostprocessorVectorStateBase() = default;
  virtual ~VectorPostprocessorVectorStateBase() = default;

  /// Whether or not this vector needs to be broadcast
  bool needs_broadcast = false;

  /// Whether or not this vector needs to be scatterd
  bool needs_scatter = false;

  /// Whether or not this vector is distributed
  bool is_distributed = false;
};

/**
 * Type specific container for VectorPostprocessor vector state
 */
template <typename T>
class VectorPostprocessorVectorState : public VectorPostprocessorVectorStateBase
{
public:
  VectorPostprocessorVectorState() = default;
  /*
  VectorPostprocessorVectorState(VectorPostprocessorVectorState && other) noexcept:
      VectorPostprocessorVectorStateBase(other)
    {
      std::cout << "state move" << std::endl;
      current = other.current;
      old = other.old;
    }
  */
  VectorPostprocessorVector<T> * current = nullptr;
  VectorPostprocessorVector<T> * old = nullptr;

  T scatter_current;
  T scatter_old;
};

/**
 * Container for storing the vectors for a VectorPostprocessor object by vector name
 */
class VectorPostprocessorStorage
{
public:
  ///@{
  // Default constructors
  VectorPostprocessorStorage(){};
  VectorPostprocessorStorage(VectorPostprocessorStorage &&) = default;
  VectorPostprocessorStorage & operator=(VectorPostprocessorStorage &&) = default;
  ///@}

  std::vector<std::unique_ptr<VectorPostprocessorVectorStateBase>> _vectors;

  /// The state (pointers to the correct data) of the vectors for the VPP object
  std::vector<std::pair<std::string, VectorPostprocessorVectorStateBase>> _values;

  /// The following flags default to false, they can each be switched to true from within the
  /// getVectorPostprocessorHelper. Once true they remain true. When they become true depends on
  /// the flag. The various getter methods should be inspected to see how they are set.

  /// Boolean indicating whether these vectors contain complete history (append mode)
  bool _contains_complete_history = false;

  /// Boolean indicating whether the vector will already be replicated in parallel by the VPP
  bool _is_broadcast = false;

  /// Boolean indicating whether any old vectors have been requested.
  bool _needs_old = false;

  /// Flag if data is distributed
  bool _is_distributed = false;
};
