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

// Level set includes
#include "LevelSetReinitializationApp.h"
#include "LevelSetReinitializationMultiApp.h"

// MOOSE includes
#include "Moose.h"
#include "MooseSyntax.h"
#include "FEProblem.h"
#include "SetupMeshAction.h"
#include "AddVariableAction.h"


template<>
InputParameters validParams<LevelSetReinitializationApp>()
{
  InputParameters params = validParams<MooseApp>();
  params.set<bool>("minimal") = true;


  //add_reinitialization_param(params);



  return params;
}

LevelSetReinitializationApp::LevelSetReinitializationApp(const InputParameters & parameters) :
    MooseApp(parameters),
    _parent_fep(getParam<FEProblem *>("_parent_fep")),
    _parent_app(_parent_fep->getMooseApp()),
    _master_awh(_parent_app.actionWarehouse())

{
  srand(processor_id());

  Moose::registerObjects(_factory);
  Moose::associateSyntax(_syntax, _action_factory);
}

void
LevelSetReinitializationApp::createMinimalApp()
{
  createMeshActions();
  createVariableActions();
  createKernelActions();
  createProblemActions();
  createUserObjectActions();
  createExecutionerActions();
  createOutputActions();
}


/*
MooseSharedPointer<MooseObjectAction>
createMooseObjectAction(const std::string & action_name, const std::string & object_name)
{



}
*/


void
LevelSetReinitializationApp::createMeshActions()
{

  {
    const SetupMeshAction & parent_action = _master_awh.getAction<SetupMeshAction>("setup_mesh");
    InputParameters action_params = parent_action.parameters();


    // Create The Action
    MooseSharedPointer<MooseObjectAction> action = MooseSharedNamespace::static_pointer_cast<MooseObjectAction>(_action_factory.create("SetupMeshAction", "Mesh", action_params));


    _action_warehouse.addActionBlock(action);
  }

  {
    const SetupMeshAction & parent_action = _master_awh.getAction<SetupMeshAction>("init_mesh");
    InputParameters action_params = parent_action.parameters();

    MooseSharedPointer<Action> action = _action_factory.create("SetupMeshAction", "Mesh", action_params);
    _action_warehouse.addActionBlock(action);
  }
}

void
LevelSetReinitializationApp::createVariableActions()
{
  std::cout << "LevelSetReinitializationApp::createVariableActions()" << std::endl;


  // Get the order and family from the parent variable
  MooseEnum families(AddVariableAction::getNonlinearVariableFamilies());
  MooseEnum orders(AddVariableAction::getNonlinearVariableOrders());
  MooseVariable & parent_var = _parent_fep->getVariable(0, getParam<VariableName>("levelset_variable"));
  families = parent_var.feType().family;
  orders = parent_var.feType().order;

  {
    InputParameters action_params = _action_factory.getValidParams("AddVariableAction");
    action_params.set<MooseEnum>("family") = families;
    action_params.set<MooseEnum>("order") = orders;
    MooseSharedPointer<Action> action = _action_factory.create("AddVariableAction", "phi", action_params);
    _action_warehouse.addActionBlock(action);
  }

  {
    InputParameters action_params = _action_factory.getValidParams("AddAuxVariableAction");
    action_params.set<MooseEnum>("family") = families;
    action_params.set<MooseEnum>("order") = orders;
    MooseSharedPointer<Action> action = _action_factory.create("AddAuxVariableAction", "AuxVariables/phi_0", action_params);
    _action_warehouse.addActionBlock(action);

  }
}

void
LevelSetReinitializationApp::createKernelActions()
{
  {
    InputParameters action_params = _action_factory.getValidParams("AddKernelAction");
    action_params.set<std::string>("type") = "TimeDerivative";

    MooseSharedPointer<MooseObjectAction> action = MooseSharedNamespace::static_pointer_cast<MooseObjectAction>(_action_factory.create("AddKernelAction", "Kernels/time", action_params));

    InputParameters & params = action->getObjectParams();
    params.set<VariableName>("variable") = "phi";
  }


  {
    InputParameters action_params = _action_factory.getValidParams("AddKernelAction");
    action_params.set<std::string>("type") = "LevelSetOlssonReinitialization";

    MooseSharedPointer<MooseObjectAction> action = MooseSharedNamespace::static_pointer_cast<MooseObjectAction>(_action_factory.create("AddKernelAction", "Kernels/olsson", action_params));

    InputParameters & params = action->getObjectParams();
    params.set<VariableName>("variable") = "phi";
    params.set<VariableName>("phi_0") = "phi_0";
    params.set<Real>("epsilon") = getParam<Real>("epsilon");
  }
}

void
LevelSetReinitializationApp::createProblemActions()
{
  // Build the Action parameters
  InputParameters action_params = _action_factory.getValidParams("CreateProblemAction");
  action_params.set<std::string>("type") = "LevelSetReinitializationProblem";

  // Create the action
  MooseSharedPointer<Action> action = _action_factory.create("CreateProblemAction", "Problem", action_params);

  // Add Action to the warehouse
  _action_warehouse.addActionBlock(action);
}

void
LevelSetReinitializationApp::createUserObjectActions()
{
  InputParameters action_params = _action_factory.getValidParams("AddUserObjectAction");
  action_params.set<std::string>("type") = "LevelSetOlssonTerminator";

  MooseSharedPointer<MooseObjectAction> action = MooseSharedNamespace::static_pointer_cast<MooseObjectAction>(_action_factory.create("AddUserObjectActions", "UserObjects/terminator", action_params));

  InputParameters & params = action->getObjectParams();
  params.set<Real>("tol") = getParam<Real>("tol");
  params.set<unsigned int>("min_steps") = getParam<unsigned int>("min_steps");

  _action_warehouse.addActionBlock(action);

}

void
LevelSetReinitializationApp::createExecutionerActions()
{
  // Build the Action parameters
  InputParameters action_params = _action_factory.getValidParams("CreateExecutionerAction");
  action_params.set<std::string>("type") = "Transient";

  // Create the action
  MooseSharedPointer<MooseObjectAction> action = MooseSharedNamespace::static_pointer_cast<MooseObjectAction>(_action_factory.create("CreateExecutionerAction", "Executioner", action_params));

    // Set the object parameters
  InputParameters & params = action->getObjectParams();
  params.set<unsigned int>("num_steps") = getParam<unsigned int>("max_steps");
  params.set<Real>("dt") = getParam<Real>("dtau");

  // Add Action to the warehouse
  _action_warehouse.addActionBlock(action);
}

void
LevelSetReinitializationApp::createOutputActions()
{
  // Build the Action parameters
  InputParameters action_params = _action_factory.getValidParams("CommonOutputAction");
  //action_params.set<bool>("console") = false;

  // Create action
  MooseSharedPointer<Action> action = _action_factory.create("CommonOutputAction", "Outputs", action_params);

  // Add Action to the warehouse
  _action_warehouse.addActionBlock(action);


}
