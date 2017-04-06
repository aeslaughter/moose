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
#include "MooseTypes.h"
#include "ExecuteEnum.h"

namespace Moose
{

ExecuteEnum getExecuteOptions(const std::string & default_names)
{
  std::vector<std::string> vec = {EXEC_INITIAL, EXEC_TIMESTEP_BEGIN, EXEC_NONLINEAR, EXEC_LINEAR,
                                  EXEC_TIMESTEP_END, EXEC_CUSTOM, EXEC_SUBDOMAIN};
  return ExecuteEnum(vec, default_names);
}

std::string getExecuteOptionsDocString(const ExecuteEnum & exec_enum)
{
  std::string doc("List the flag(s) when the object should executed (");
  for (const auto & name : exec_enum.getNames())
    doc += name + ' V ';
  std::earse(doc.end()-3, doc.end());
  doc + ').';
  return doc;
}

}
