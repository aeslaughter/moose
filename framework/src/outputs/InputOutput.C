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
#include "Conversion.h"
#include "parse.h"

#include "KernelBase.h"
#include "GeneralDamper.h"
#include "ElementDamper.h"
#include "NodalDamper.h"
#include "Marker.h"
#include "Indicator.h"

#include "SetAdaptivityOptionsAction.h"

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

  hit::Section * root = new hit::Section("");

  // Adaptivity
  hit::Node * node = addSystem<SetAdaptivityOptionsAction>("Adaptivity", root);
  if (node)
  {
    addSystem<Marker>("Markers", node, _problem_ptr->getMarkerWarehouse());
    addSystem<Marker>("Indicators", node, _problem_ptr->getIndicatorWarehouse());
  }

  addSystem<KernelBase>("Kernels", root, _problem_ptr->getNonlinearSystem().getKernelWarehouse());

  // Dampers
  const MooseObjectWarehouseBase<GeneralDamper> & general_dampers = _problem_ptr->getNonlinearSystem().getGeneralDamperWarehouse();
  const MooseObjectWarehouseBase<ElementDamper> & element_dampers = _problem_ptr->getNonlinearSystem().getElementDamperWarehouse();
  const MooseObjectWarehouseBase<NodalDamper> & nodal_dampers = _problem_ptr->getNonlinearSystem().getNodalDamperWarehouse();
  if (general_dampers.hasObjects() || element_dampers.hasObjects() || nodal_dampers.hasObjects())
  {
    hit::Node * dampers = addSystem("Dampers", root);
    addObjects<GeneralDamper>(dampers, general_dampers);
    addObjects<ElementDamper>(dampers, element_dampers);
    addObjects<NodalDamper>(dampers, nodal_dampers);
  }



  std::cout << root->render() << std::endl;
  delete root;
}

hit::Node *
InputOutput::addSystem(const std::string & name, hit::Node * parent)
{
  hit::Section * node = new hit::Section(name);
  parent->addChild(node);
  return node;
}

/*
hit::Node *
InputOutput::addSystem(const std::string & name, hit::Node * parent, const std::string & action_name)
{
  for ()

  return nullptr;
}
*/

void
InputOutput::addParameterNode(const std::string & name, libMesh::Parameters::Value * value, hit::Node * parent, const InputParameters & parameters)
{
  if (!parameters.isPrivate(name) && parameters.isParamSetByUser(name))
  {
  //  if (name[0] == '_')
  //    mooseWarning("The parameter '", name, "' begins with and underscore but it is not private.");

    std::string param_string; // the parameter string to output

    // Special case for bool parameters
    auto param_bool = dynamic_cast<InputParameters::Parameter<bool> *>(value);
    if (param_bool)
      param_string = param_bool->get() ? "true" : "false";

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
