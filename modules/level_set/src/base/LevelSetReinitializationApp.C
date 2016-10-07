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
  InputParameters params = validParams<LevelSetApp>();
  params.set<bool>("minimal") = true;


  // add_reinitialization_param(params);



  return params;
}

LevelSetReinitializationApp::LevelSetReinitializationApp(const InputParameters & parameters) :
    LevelSetApp(parameters),
    _parent_fep(getParam<FEProblem *>("_parent_fep")),
    _parent_app(_parent_fep->getMooseApp()),
    _master_awh(_parent_app.actionWarehouse())

{
}

void
LevelSetReinitializationApp::createMinimalApp()
{
  createMeshActions();
  createExecutionerActions();
  createProblemActions();


  createVariableActions();
  createKernelActions();
//  createUserObjectActions();
  createOutputActions();

  _action_warehouse.build();
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
    // Build the Action parameters
    InputParameters action_params = _action_factory.getValidParams("SetupMeshAction");
    action_params.set<std::string>("type") = "GeneratedMesh";
    action_params.set<std::string>("task") = "setup_mesh";

    // Create The Action
    MooseSharedPointer<MooseObjectAction> action = MooseSharedNamespace::static_pointer_cast<MooseObjectAction>(_action_factory.create("SetupMeshAction", "Mesh", action_params));

    // Set the object parameters
    InputParameters & params = action->getObjectParams();
    params.set<MooseEnum>("dim") = "1";
    params.set<unsigned int>("nx") = 1;

    // Add Action to the warehouse
    _action_warehouse.addActionBlock(action);
  }

  // SetupMeshAction (init_mesh)
  {
    // Action parameters
    InputParameters action_params = _action_factory.getValidParams("SetupMeshAction");
    action_params.set<std::string>("type") = "GeneratedMesh";
    action_params.set<std::string>("task") = "init_mesh";

    // Build the action
    MooseSharedPointer<Action> action = _action_factory.create("SetupMeshAction", "Mesh", action_params);
    _action_warehouse.addActionBlock(action);
  }


  /*
  for (auto parent_action_ptr : _master_awh.getActionsByName("setup_mesh"))
  {
    // InputParameters action_params = parent_action_ptr->parameters();
    // MooseSharedPointer<Action> action = _action_factory.create("SetupMeshAction", "Mesh", action_params);
    _action_warehouse.addActionBlock(MooseSharedPointer<Action>(parent_action_ptr));
  }

  for (auto parent_action_ptr : _master_awh.getActionsByName("init_mesh"))
  {
    // InputParameters action_params = parent_action_ptr->parameters();
    // MooseSharedPointer<Action> action = _action_factory.create("SetupMeshAction", "Mesh", action_params);
    //  _action_warehouse.addActionBlock(action);
    _action_warehouse.addActionBlock(MooseSharedPointer<Action>(parent_action_ptr));
  }
  */
}

void
LevelSetReinitializationApp::createVariableActions()
{
  std::cout << "LevelSetReinitializationApp::createVariableActions()" << std::endl;


  // Get the order and family from the parent variable
  MooseEnum families(AddVariableAction::getNonlinearVariableFamilies());
  MooseEnum orders(AddVariableAction::getNonlinearVariableOrders());
  MooseVariable & parent_var = _parent_fep->getVariable(0, "phi");// getParam<VariableName>("levelset_variable"));
  // families = parent_var.feType().family;
  //orders = parent_var.feType().order;

  {
    InputParameters action_params = _action_factory.getValidParams("AddVariableAction");
    action_params.set<MooseEnum>("family") = "lagrange";//families;
    action_params.set<MooseEnum>("order") = "first";//orders;
    MooseSharedPointer<Action> action = _action_factory.create("AddVariableAction", "phi", action_params);
    _action_warehouse.addActionBlock(action);
  }

  {
    InputParameters action_params = _action_factory.getValidParams("AddAuxVariableAction");
    action_params.set<MooseEnum>("family") = "lagrange";//families;
    action_params.set<MooseEnum>("order") = "first";//orders;
    MooseSharedPointer<Action> action = _action_factory.create("AddAuxVariableAction", "phi_0", action_params);
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
    params.set<NonlinearVariableName>("variable") = "phi";

    _action_warehouse.addActionBlock(action);
  }


  {
    InputParameters action_params = _action_factory.getValidParams("AddKernelAction");
    action_params.set<std::string>("type") = "LevelSetOlssonReinitialization";

    MooseSharedPointer<MooseObjectAction> action = MooseSharedNamespace::static_pointer_cast<MooseObjectAction>(_action_factory.create("AddKernelAction", "Kernels/olsson", action_params));

    InputParameters & params = action->getObjectParams();
    params.set<NonlinearVariableName>("variable") = "phi";
    params.set<std::vector<VariableName>>("phi_0") = std::vector<VariableName>(1,"phi_0");
    //x params.set<PostprocessorName>("epsilon") = "0.03";//getParam<Real>("epsilon");

    _action_warehouse.addActionBlock(action);

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
  params.set<unsigned int>("min_steps") = 3;//getParam<unsigned int>("min_steps");

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
  params.set<unsigned int>("num_steps") = 10;//getParam<unsigned int>("max_steps");
  params.set<Real>("dt") = 1;//getParam<Real>("dtau");

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
