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
#include "MooseObjectWarehouseBase.h"
#include "KernelBase.h"
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
  addSubSectionNodes<KernelBase>("Kernels", _problem_ptr->getNonlinearSystem().getKernelWarehouse(), &root);



  //hit::Section node("Kernels");
  //root.addChild(&node);

  /*
  const MooseObjectWarehouse<KernelBase> & warehouse = _problem_ptr->getNonlinearSystem().getKernelWarehouse();
  const std::vector<std::shared_ptr<KernelBase>> & kernels = warehouse.getObjects();
  for (const std::shared_ptr<KernelBase> & kernel : kernels)
  {
    hit::Section * sub_section = new hit::Section(kernel->name());
    node.addChild(sub_section);

    for (const auto & map_pair : kernel->parameters())
      addParameterNodes(map_pair.first, map_pair.second, sub_section, kernel->parameters());
    }
    */



  std::cout << root.render() << std::endl;
}

void
InputOutput::addParameterNodes(const std::string & name, libMesh::Parameters::Value * value, hit::Node * parent, const InputParameters & parameters)
{
  /*
  std::string syntax;
  if (parameters.isParamValid("parser_syntax"))
  {
    syntax = parameters.get<std::string>("parser_syntax");
    std::cout << "syntax = " << syntax << std::endl;
  }
  */

  if (!parameters.isPrivate(name) && parameters.isParamValid(name))
  {
    /*
    if (param_name == "control_tags")
    {
      // deal with the control tags. The current parser_syntax is automatically added to this. So
      // we can remove the parameter if that's all there is in it
    }
    else
    */
    {
      // special treatment for some types
      auto param_bool = dynamic_cast<InputParameters::Parameter<bool> *>(value);

      // parameter value
      std::string param_string;
      if (param_bool)
        param_string = param_bool->get() ? "true" : "false";
      else
      {
        std::stringstream ss;
        value->print(ss);
        param_string = MooseUtils::trim(ss.str());
      }

      // delete trailing space

      //if (param_value.back() == ' ')
      //  param_value.pop_back();

      // add quotes if the parameter contains spaces
      if (param_string.find_first_of(" ") != std::string::npos)
        param_string = "'" + param_string + "'";


      hit::Field * field = new hit::Field(name, hit::Field::Kind::String, param_string);
      parent->addChild(field);

    }
  }

}

/*
template<class T>
void
InputOutput::addSubSectionNodes(const std::string & name, const MooseObjectWarehouseBase<T> & warehouse, hit::Node * parent)
{
  const std::vector<std::shared_ptr<T>> & objects = warehouse.getObjects();
  for (const std::shared_ptr<T> & object_ptr : objects)
  {
    hit::Section * sub_section = new hit::Section(object_ptr->name());
    parent->addChild(sub_section);
    for (const auto & map_pair : object_ptr->parameters())
      addParameterNodes(map_pair.first, map_pair.second, sub_section, object_ptr->parameters());
}
*/


/*
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
*/
