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
#include "Control.h"
#include "ExecuteEnum.h"

template <>
InputParameters
validParams<Control>()
{
  InputParameters params = validParams<MooseObject>();
  params += validParams<TransientInterface>();
  params += validParams<SetupInterface>();
  params += validParams<FunctionInterface>();
  params.registerBase("Control");

  ExecuteEnum & exec_enum = params.set<ExecuteEnum>("execute_on");
  exec_enum.extend("subdomain");
  exec_enum = "initial timestep_end";
  params.setDocString("execute_on", exec_enum.getDocString());

  return params;
}

Control::Control(const InputParameters & parameters)
  : MooseObject(parameters),
    TransientInterface(this),
    SetupInterface(this),
    FunctionInterface(this),
    UserObjectInterface(this),
    PostprocessorInterface(this),
    VectorPostprocessorInterface(this),
    _fe_problem(*parameters.get<FEProblemBase *>("_fe_problem_base")),
    _input_parameter_warehouse(_app.getInputParameterWarehouse())
{
}
