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
#include "InputOutput.h"
#include "FEProblemBase.h"
#include "NonlinearSystem.h"
#include "MooseObjectWarehouse.h"
#include "parse.h"

template <>
InputParameters
validParams<InputOutput>()
{
  InputParameters params = validParams<FileOutput>();
  params.set<ExecFlagEnum>("execute_on") = EXEC_INITIAL;
  return params;
}

InputOutput::InputOutput(const InputParameters & parameters) : FileOutput(parameters) {}

std::string
InputOutput::filename()
{
  return _file_base + ".i";
}

void
InputOutput::output(const ExecFlagType & /*type*/)
{
  hit::Section root("");

  hit::Section node("Kernels");
  root.addChild(&node);

  const MooseObjectWarehouse<KernelBase> & warehouse = _problem_ptr->getNonlinearSystem().getKernelWarehouse();
  const std::vector<std::shared_ptr<KernelBase>> & kernels = warehouse.getObjects();
  //for (const auto & kernel : kernels)



  std::cout << root.render() << std::endl;
}



std::map<std::string, std::string>
InputOutput::stringifyParameters(const InputParameters & parameters)
{
  std::map<std::string, std::string> parameter_map;

  std::string syntax;
  if (parameters.isParamValid("parser_syntax"))
    syntax = parameters.get<std::string>("parser_syntax");

  for (auto & value_pair : parameters)
  {
    // parameter name
    const auto & param_name = value_pair.first;

    if (!parameters.isPrivate(param_name) && parameters.isParamValid(param_name))
    {
      if (param_name == "control_tags")
      {
        // deal with the control tags. The current parser_syntax is automatically added to this. So
        // we can remove the parameter if that's all there is in it
      }
      else
      {
        // special treatment for some types
        auto param_bool = dynamic_cast<InputParameters::Parameter<bool> *>(value_pair.second);

        // parameter value
        std::string param_value;
        if (param_bool)
          param_value = param_bool->get() ? "true" : "false";
        else
        {
          std::stringstream ss;
          value_pair.second->print(ss);
          param_value = ss.str();
        }

        // delete trailing space
        if (param_value.back() == ' ')
          param_value.pop_back();

        // add quotes if the parameter contains spaces
        if (param_value.find_first_of(" ") != std::string::npos)
          param_value = "'" + param_value + "'";

        parameter_map[param_name] = param_value;
      }
    }
  }

  return parameter_map;
}
