/****************************************************************/
/*               DO NOT MODIFY THIS HEADER                      */
/* MOOSE - Multiphysics Object Oriented Simulation Environment  */
/*                                                              */
/*           (c) 2010 Battelle Energy Alliance, LLC             */
/*                   ALL RIGHTS RESERVED                        */
/*                                                              */
/*          Prepared by Battelle Energy Alliance, LLC           */
/*            Under Contract No. DE-AC07-05ID14517              */
/*            With the U. S. Department of Energy               */
/*                                                              */
/*            See COPYRIGHT for full restrictions               */
/****************************************************************/

#ifndef EXECFLAGENUM_H
#define EXECFLAGENUM_H

// MOOSE includes
#include "MultiMooseEnum.h"

// Forward declarations
class ExecFlagEnum;

/**
 * A MultiMooseEnum object to hold "execute_on" flags.
 *
 * This object allows available flags to be added or removed thus each object can control the
 * flags that are available.
 */
class ExecFlagEnum : public MultiMooseEnum
{
public:
  using MultiMooseEnum::operator=;

  /**
   * Construct an object with the default flags available, see ExecFlagEnum.C.
   */
  ExecFlagEnum();

  /**
   * Same as above but the flags provided are set as current.
   */
  ExecFlagEnum(const std::vector<ExecFlagType> & current);

  /**
   * Add additional execute_on flags to the list of possible flags.
   *
   * This does not set the supplied, the MultiMooseEnum::set() method should be used for making
   * flags current.
   */
  void addAvailableFlags(const std::set<ExecFlagType> & flags);

  /**
   * Remove flags from being available.
   */
  void removeAvailableFlags(const std::set<ExecFlagType> & flags);

  /**
   * Generate a documentation string for the "execute_on" parameter.
   */
  std::string getExecuteOnDocString();

  /**
   * Reference the all the available items.
   */
  const std::set<ExecFlagType> & items(){ return _items; }
};

#endif
