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

#ifndef EXECUTEONENUM_H
#define EXECUTEONENUM_H

// MOOSE includes
#include "MultiMooseEnum.h"

/**
 * An extendable MultiMooseEnum to allow for execution flag customization.
 */
class ExecuteOnEnum : public MultiMooseEnum
{
public:
  ExecuteOnEnum(std::string names, std::string default_names);
  ExecuteOnEnum(std::vector<std::string> names, std::string default_names);

  /**
   * Adds an additional possible enumeration value.
   * @params name The name of enumeration value to add, it can include a numeric value
   * (e.g. "combo=12345")
   *
   * For example the following creates a ExecuteEnum that has three possible settings: "one", "two",
   * and/or "three".
   *     ExecuteEnum ex("one two", "one");
   *     ex.extend("three");
   */
  void extend(const std::string & name);

  ///@{
  /**
   * Assignment M
   * @param names A string, set, or vector representing the enumeration values.
   * @return A reference to this object for chaining.
   */
  ExecuteOnEnum & operator=(const std::string & names);
  ExecuteOnEnum & operator=(const std::vector<std::string> & names);
  ExecuteOnEnum & operator=(const std::set<std::string> & names);
  ///@}

  // InputParameters and Output is allowed to create an empty enum but is responsible for
  // filling it in after the fact
  friend class libMesh::Parameters;

private:
  /**
   * Private constructor for use by libmesh::Parameters
   */
  ExecuteOnEnum();
};

#endif
