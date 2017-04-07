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
#include "ExecuteEnum.h"
#include "MooseUtils.h"

ExecuteEnum::ExecuteEnum(std::string names, std::string default_names)
  : MultiMooseEnum(names, default_names)
{
}

ExecuteEnum::ExecuteEnum(std::vector<std::string> names, std::string default_names)
  : MultiMooseEnum("", default_names)
{
  for (const std::string & raw_name : names)
    addEnumerationName(raw_name);
}

ExecuteEnum::ExecuteEnum() : MultiMooseEnum(){}

void
ExecuteEnum::extend(const std::string & names)
{
  fillNames(names);
}

ExecuteEnum &
ExecuteEnum::operator=(const std::string & names)
{
  MultiMooseEnum::operator=(names);
  return *this;
}

ExecuteEnum &
ExecuteEnum::operator=(const std::vector<std::string> & names)
{
  MultiMooseEnum::operator=(names);
  return *this;
}

ExecuteEnum &
ExecuteEnum::operator=(const std::set<std::string> & names)
{
  MultiMooseEnum::operator=(names);
  return *this;
}
