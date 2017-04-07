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

#include "SetupInterface.h"
#include "Conversion.h"
#include "FEProblem.h"
#include "ExecuteEnum.h"

template <>
InputParameters
validParams<SetupInterface>()
{
  InputParameters params = emptyInputParameters();

  // Get an MooseEnum of the available 'execute_on' options
  ExecuteEnum execute_options(Moose::getExecuteOptions(EXEC_LINEAR));
  std::string exec_doc = Moose::getExecuteOptionsDocString(execute_options);

  // Add the 'execute_on' input parameter for users to set
  params.addParam<ExecuteEnum>("execute_on", execute_options, exec_doc);

  // The Output system uses different options for the 'execute_on' than other systems, therefore the
  // check of the options
  // cannot occur based on the 'execute_on' parameter, so this flag triggers the check
//  params.addPrivateParam<bool>("check_execute_on", true);

  return params;
}

SetupInterface::SetupInterface(const MooseObject * moose_object)
  : _exec_enum(moose_object->parameters().get<ExecuteEnum>("execute_on")),
    _exec_flags(_exec_enum.begin(), _exec_enum.end()),
    _current_execute_flag(
        (moose_object->parameters().getCheckedPointerParam<FEProblemBase *>("_fe_problem_base"))
            ->getCurrentExecuteOnFlag())
{

  //const InputParameters & params = moose_object->parameters();

  /**
   * While many of the MOOSE systems inherit from this interface, it doesn't make sense for them all
   * to adjust their execution flags.
   * Our way of dealing with this is by not having those particular classes add the this classes
   * valid params to their own.  In
   * those cases it won't exist so we just set it to a default and ignore it.
   */

  /*
  if (params.have_parameter<bool>("check_execute_on") && params.get<bool>("check_execute_on"))
  {
    MultiMooseEnum flags = params.get<ExecuteEnum>("execute_on");
    _exec_flags = Moose::vectorStringsToEnum<ExecFlagType>(flags);
  }

  else
    _exec_flags.push_back(EXEC_LINEAR);
  */
}

SetupInterface::~SetupInterface() {}

void
SetupInterface::initialSetup()
{
}

void
SetupInterface::timestepSetup()
{
}

void
SetupInterface::jacobianSetup()
{
}

void
SetupInterface::residualSetup()
{
}

void
SetupInterface::subdomainSetup()
{
}

const std::set<ExecFlagType> &
SetupInterface::execFlags() const
{
  return _exec_flags;
}

MultiMooseEnum
SetupInterface::getExecuteOptions()
{
  mooseDeprecated("The used of a MultiMooseEnum for the \"execute_on\" settings is deprecated.\n",
                  "The code should be updated to utilize a ExecuteEnum and the "
                  "Moose::getExecuteOptions() defined in MooseTypes.h/C.");
  return MultiMooseEnum("none=0x00 initial=0x01 linear=0x02 nonlinear=0x04 timestep_end=0x08 "
                        "timestep_begin=0x10 custom=0x100",
                        "linear");
}
