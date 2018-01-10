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
#include "InputParameterWarehouse.h"
#include "FEProblemBase.h"
#include "Conversion.h"
#include "parse.h"

#include "SetAdaptivityOptionsAction.h"
#include "CreateProblemAction.h"
#include "AddVariableAction.h"
#include "AddAuxVariableAction.h"

template <>
InputParameters
validParams<InputOutput>()
{
  InputParameters params = validParams<FileOutput>();
  params.set<ExecFlagEnum>("execute_on") = EXEC_INITIAL;
  return params;
}

InputOutput::InputOutput(const InputParameters & parameters) : FileOutput(parameters)
{
  // Create a map from "_moose_base" to the necessary syntax for re-creating input file. The
  // pair contains two pieces of information: the parent input file syntax for the parameters
  // and a bool indicating if the object is created in a sub-block (true).
  // TODO: There should be a way to get this info from the action warehouse
  _base_to_syntax["Output"] = std::make_pair("Outputs", true);
  _base_to_syntax["Kernel"] = std::make_pair("Kernels", true);
  _base_to_syntax["AuxKernel"] = std::make_pair("AuxKernels", true);
  _base_to_syntax["ScalarKernel"] = std::make_pair("ScalarKernels", true);
  _base_to_syntax["AuxScalarKernel"] = std::make_pair("AuxScalarKernels", true);
  _base_to_syntax["Marker"] = std::make_pair("Adaptivity/Markers", true);
  _base_to_syntax["BoundaryCondition"] = std::make_pair("BCs", true);
  _base_to_syntax["Function"] = std::make_pair("Functions", true);
  _base_to_syntax["InitialCondition"] = std::make_pair("ICs", true);
  _base_to_syntax["ScalarInitialCondition"] = std::make_pair("ScarlarICs", true);
  _base_to_syntax["Postprocessor"] = std::make_pair("Postprocessors", true);
  _base_to_syntax["VectorPostprocessor"] = std::make_pair("VectorPostprocessors", true);
  _base_to_syntax["MoosePreconditioner"] = std::make_pair("Preconditioner", true);
  _base_to_syntax["Material"] = std::make_pair("Materials", true);

  _base_to_syntax["Executioner"] = std::make_pair("Executioner", false);
  _base_to_syntax["TimeStepper"] = std::make_pair("Executioner/TimeStepper", false);
  _base_to_syntax["TimeIntegrator"] = std::make_pair("Executioner/TimeIntegrator", false);

  _base_to_syntax["MooseMesh"] = std::make_pair("Mesh", false);
  _base_to_syntax["Problem"] = std::make_pair("Problem", false);

}

std::string
InputOutput::filename()
{
  return _app.getInputFileName() + ".out";
}

void
InputOutput::output(const ExecFlagType & /*type*/)
{
  // Create a unique set of InputParamter objects
  InputParameterWarehouse & warehouse = _app.getInputParameterWarehouse();
  std::set<std::shared_ptr<InputParameters>> parameters;
  for (auto & map_pair : warehouse.getInputParameters())
    parameters.insert(map_pair.second);

  // Loop over all the InputParamter objects and add the parameters to the hit tree
  hit::Section * root = new hit::Section("");
  for (const std::shared_ptr<InputParameters> params : parameters)
    addInputParameters(root, params);

  // It is possible to loop over actions and get the parameters for each action and task, but
  // the purpose of this object is to explode the objects and not rely on the actions. The following
  // calls are as minimal as possible to re-run the input file.
  //addActionSyntax<CreateProblemAction>("Problem", root);
  addActionSyntax<SetAdaptivityOptionsAction>("Adaptivity", root);
  addActionSyntax<AddVariableAction>("Variables", root, /*create_sections = */true);
  addActionSyntax<AddAuxVariableAction>("AuxVariables", root, /*create_sections = */true);

  // Explode and write the tree to a file
  hit::Node * node = hit::explode(root);
  std::ofstream outfile;
  outfile.open(filename());
  outfile << node->render() << std::endl;
  outfile.close();
  std::cout << node->render() << std::endl;
  delete root;
}

void
InputOutput::addInputParameters(hit::Node * root, std::shared_ptr<InputParameters> params)
{
  const std::string & base = params->get<std::string>("_moose_base");
  const std::string & name = params->get<std::string>("_object_name");

  std::map<std::string, std::pair<std::string, bool>>::const_iterator iter = _base_to_syntax.find(base);
  if (iter != _base_to_syntax.end())
  {
    hit::Section * node;
    if (iter->second.second)
      node = new hit::Section(iter->second.first + '/' + name);
    else
      node = new hit::Section(iter->second.first);

    root->addChild(node);
    for (const auto & param_map_pair : *params)
      addParameter(param_map_pair.first, param_map_pair.second, node, *params);
  }

  else
    mooseError("The object named '", name,"' has a base name ('", base, "') without a syntax entry for reproducing the object input file syntax.");
}

void
InputOutput::addParameter(const std::string & name, libMesh::Parameters::Value * value, hit::Node * parent, const InputParameters & parameters)
{
  if (!parameters.isPrivate(name) && parameters.isParamSetByUser(name))
  {
    if (name[0] == '_')
      return;
  //    mooseWarning("The parameter '", name, "' begins with and underscore but it is not private.");

    std::string param_string; // the parameter string to output

    // Special case for bool parameters
    auto param_bool = dynamic_cast<InputParameters::Parameter<bool> *>(value);
    auto param_realvec = dynamic_cast<InputParameters::Parameter<RealVectorValue> *>(value);
    if (param_bool)
      param_string = param_bool->get() ? "true" : "false";

    else if (param_realvec)
    {
      std::stringstream ss;
      param_realvec->get().write_unformatted(ss);
      param_string = MooseUtils::trim(ss.str());
    }

    // Remove "control_tags" added by MOOSE
    else if (name == "control_tags" && parameters.isParamValid("parser_syntax"))
    {
      std::string tag = MooseUtils::baseName(parameters.get<std::string>("parser_syntax"));
      std::vector<std::string> tags;
      for (const auto & t : parameters.get<std::vector<std::string>>("control_tags"))
        if (t != tag)
          tags.push_back(t);

      param_string = Moose::stringify(tags);
    }

    // General case
    else
    {
      std::stringstream ss;
      value->print(ss);
      param_string = MooseUtils::trim(ss.str());
    }

    // Create the parameter node
    if (!param_string.empty())
    {
      // If spaces exists add quotes
      if (param_string.find_first_of(" ") != std::string::npos)
        param_string = "'" + param_string + "'";

      hit::Field * field = new hit::Field(name, hit::Field::Kind::String, param_string);
      parent->addChild(field);
    }
  }
}
