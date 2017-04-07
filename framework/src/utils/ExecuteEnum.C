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


ExecuteEnum::ExecuteEnum(std::string names, std::string default_names)
  : MultiMooseEnum(names, default_names)
{
}

ExecuteEnum::ExecuteEnum(const ExecuteEnum & other_enum)
  : MultiMooseEnum(other_enum)
{
}

ExecuteEnum::ExecuteEnum() {}

void
ExecuteEnum::extend(const std::string & name)
{
  fillNames(name);
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

std::string
ExecuteEnum::getDocString()
{
  std::string doc("The list of flag(s) indicating when this object should executed (\"");
  for (const auto & name : _names)
    doc += name + "\" V \"";
  doc.erase(doc.end()-5, doc.end());
  doc += "\").";
  return doc;
}

const std::set<std::string> &
ExecuteEnum::current() const
{
  return _current_names;
}
