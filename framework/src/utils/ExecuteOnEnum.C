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

// MOOSE includes
#include "ExecuteOnEnum.h"
#include "MooseUtils.h"

ExecuteOnEnum::ExecuteOnEnum(std::string names, std::string default_names)
  : MultiMooseEnum(names, default_names)
{
}

ExecuteOnEnum::ExecuteOnEnum(std::vector<std::string> names, std::string default_names)
  : MultiMooseEnum("", default_names)
{
  for (const std::string & raw_name : names)
    addEnumerationName(raw_name);
}

ExecuteOnEnum::ExecuteOnEnum() : MultiMooseEnum() {}

void
ExecuteOnEnum::extend(const std::string & names)
{
  fillNames(names);
}

ExecuteOnEnum &
ExecuteOnEnum::operator=(const std::string & names)
{
  MultiMooseEnum::operator=(names);
  return *this;
}

ExecuteOnEnum &
ExecuteOnEnum::operator=(const std::vector<std::string> & names)
{
  MultiMooseEnum::operator=(names);
  return *this;
}

ExecuteOnEnum &
ExecuteOnEnum::operator=(const std::set<std::string> & names)
{
  MultiMooseEnum::operator=(names);
  return *this;
}
