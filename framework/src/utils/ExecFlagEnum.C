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

#include "ExecFlagEnum.h"
#include "MooseError.h"

ExecFlagEnum::ExecFlagEnum() : MultiMooseEnum()
{
  // Add the default execution flags
  addAvailableFlags({EXEC_NONE,
                     EXEC_INITIAL,
                     EXEC_LINEAR,
                     EXEC_NONLINEAR,
                     EXEC_TIMESTEP_END,
                     EXEC_TIMESTEP_BEGIN,
                     EXEC_CUSTOM});
}

ExecFlagEnum::ExecFlagEnum(const std::vector<ExecFlagType> & current) : ExecFlagEnum()
{
  setCurrentItems(current);
}

void
ExecFlagEnum::addAvailableFlags(const std::set<ExecFlagType> & flags)
{
  _items.insert(flags.begin(), flags.end());
}

void
ExecFlagEnum::removeAvailableFlags(const std::set<ExecFlagType> & flags)
{
  for (const auto & item : flags)
    if (find(item) == _items.end())
      mooseError("The supplied item '",
                 item,
                 "' is not an available enum item for the "
                 "MultiMooseEnum object, thus it cannot be removed.");
    else if (contains(item))
      mooseError("The supplied item '", item, "' is a selected item, thus it can not be removed.");

  _items.erase(flags.begin(), flags.end());
}

std::string
ExecFlagEnum::getExecuteOnDocString()
{
  std::string doc("The list of flag(s) indicating when this object should be executed, the "
                  "available options include \'");
  for (const std::string & name : getNames())
    doc += name + "', '";
  doc.erase(doc.end() - 4, doc.end());
  doc += "').";
  return doc;
}
