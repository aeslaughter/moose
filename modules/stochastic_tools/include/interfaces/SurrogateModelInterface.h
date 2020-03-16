//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#pragma once

#include "ParallelUniqueId.h"
#include "InputParameters.h"
#include "FEProblemBase.h"

// Forward declarations
class SurrogateModel;
class SurrogateModelInterface;

template <>
InputParameters validParams<SurrogateModelInterface>();

/**
 * Interface for objects that need to use samplers.
 *
 * This practically adds two methods for getting SurrogateModel objects:
 *
 *  1. Call `getSurrogateModel` or `getSurrogateModelByName` without a template parameter and you
 * will get a `SurrogateModel` base object (see SurrogateModelInterface.C for the template
 * specialization).
 *  2. Call `getSurrogateModel<MySurrogateModel>` or `getSurrogateModelByName<MySurrogateModel>` to
 * perform a cast to the desired type, as done for UserObjects.
 */
class SurrogateModelInterface
{
public:
  static InputParameters validParams();

  /**
   * @param params The parameters used by the object being instantiated. This
   *        class needs them so it can get the sampler named in the input file,
   *        but the object calling getSurrogateModel only needs to use the name on the
   *        left hand side of the statement "sampler = sampler_name"
   */
  SurrogateModelInterface(const MooseObject * moose_object);

  /**
   * Get a sampler with a given name
   * @param name The name of the parameter key of the sampler to retrieve
   * @return The sampler with name associated with the parameter 'name'
   */
  template <typename T = SurrogateModel>
  T & getSurrogateModel(const std::string & name);

  /**
   * Get a sampler with a given name
   * @param name The name of the sampler to retrieve
   * @return The sampler with name 'name'
   */
  template <typename T = SurrogateModel>
  T & getSurrogateModelByName(const UserObjectName & name);

private:
  /// Parameters of the object with this interface
  const InputParameters & _smi_params;

  /// Reference to FEProblemBase instance
  FEProblemBase & _smi_feproblem;

  /// Thread ID
  THREAD_ID _smi_tid;
};

template <typename T>
T &
SurrogateModelInterface::getSurrogateModel(const std::string & name)
{
  return getSurrogateModelByName<T>(_smi_params.get<UserObjectName>(name));
}

template <typename T>
T &
SurrogateModelInterface::getSurrogateModelByName(const UserObjectName & name)
{
  SurrogateModel * base_ptr = &_smi_feproblem.getUserObjectTempl<T>(name, _smi_tid);
  T * obj_ptr = dynamic_cast<T *>(base_ptr);
  if (!obj_ptr)
    mooseError(
        "Failed to find a SurrogateModel object with the name '", name, "' for the desired type.");
  return *obj_ptr;
}
