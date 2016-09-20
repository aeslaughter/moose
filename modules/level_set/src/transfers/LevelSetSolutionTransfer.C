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
#include "LevelSetSolutionTransfer.h"
#include "MooseTypes.h"
#include "FEProblem.h"
#include "DisplacedProblem.h"
#include "MultiApp.h"
#include "MooseMesh.h"
#include "NonlinearSystem.h"

// libMesh includes
#include "libmesh/system.h"
#include "libmesh/mesh_tools.h"
#include "libmesh/id_types.h"

template<>
InputParameters validParams<LevelSetSolutionTransfer>()
{
  InputParameters params = validParams<MultiAppTransfer>();
  params.addRequiredParam<VariableName>("to_variable", "The variable that the solution is being transfered into.");
  params.addRequiredParam<VariableName>("from_variable", "The variable to transfer from.");

  return params;
}

LevelSetSolutionTransfer::LevelSetSolutionTransfer(const InputParameters & parameters) :
    MultiAppTransfer(parameters),
    _to_var_name(getParam<VariableName>("to_variable")),
    _from_var_name(getParam<VariableName>("from_variable"))
{
  // This transfer does not work with DistributedMesh
  _fe_problem.mesh().errorIfDistributedMesh("LevelSetSolutionTransfer");
}

void
LevelSetSolutionTransfer::initialSetup()
{
  variableIntegrityCheck(_to_var_name);
}

void
LevelSetSolutionTransfer::transfer(FEProblem & to_problem, FEProblem & from_problem)
{
  MPI_Comm swapped = Moose::swapLibMeshComm(_multi_app->comm());

  System * to_sys = find_sys(to_problem.es(), _to_var_name);


  MooseVariable & from_var = from_problem.getVariable(0, _from_var_name);
  MeshBase * from_mesh = &from_problem.mesh().getMesh();
  SystemBase & from_system_base = from_var.sys();
  System & from_sys = from_system_base.system();
  unsigned int from_sys_num = from_sys.number();


  // Only works with a serialized mesh to transfer from!
  mooseAssert(from_sys.get_mesh().is_serial(), "LevelSetSolutionTransfer only works with ReplicatedMesh!");

  unsigned int from_var_num = from_sys.variable_number(from_var.name());


  unsigned int sys_num = to_sys->number();
  unsigned int var_num = to_sys->variable_number(_to_var_name);

  NumericVector<Real> & solution = to_problem.getNonlinearSystem().hasVariable(_to_var_name) ? to_problem.getNonlinearSystem().solution() : to_problem.getAuxiliarySystem().solution();
  MeshBase * mesh = &to_problem.mesh().getMesh();

  bool is_nodal = to_sys->variable_type(var_num).family == LAGRANGE;

  if (is_nodal)
  {
    MeshBase::const_node_iterator node_it = mesh->local_nodes_begin();
    MeshBase::const_node_iterator node_end = mesh->local_nodes_end();

    for (; node_it != node_end; ++node_it)
    {
      Node * node = *node_it;
      unsigned int node_id = node->id();

      if (node->n_dofs(sys_num, var_num) > 0) // If this variable has dofs at this node
      {
        // The zero only works for LAGRANGE!
        dof_id_type dof = node->dof_number(sys_num, var_num, 0);

        // Swap back
        Moose::swapLibMeshComm(swapped);

        Node * from_node = from_mesh->node_ptr(node_id);

        // Assuming LAGRANGE!
        dof_id_type from_dof = from_node->dof_number(from_sys_num, from_var_num, 0);
        //Real from_value = (*serialized_solution)(from_dof);
        Real from_value = (*from_sys.solution)(from_dof);

        // Swap again
        swapped = Moose::swapLibMeshComm(_multi_app->comm());

        solution.set(dof, from_value);
      }
    }
  }
  else // Elemental
  {
    mooseError("LevelSetSolutionTransfer can only be used on nodal variables");
  }

  solution.close();
  to_sys->update();

  // Swap back
  Moose::swapLibMeshComm(swapped);
}

void
LevelSetSolutionTransfer::execute()
{
  _console << "Beginning LevelSetSolutionTransfer " << name() << std::endl;

  if (_direction == TO_MULTIAPP)
  {
    FEProblem & from_problem = _multi_app->problem();
    for (unsigned int i = 0; i < _multi_app->numGlobalApps(); i++)
    if (_multi_app->hasLocalApp(i))
      transfer(_multi_app->appProblem(i), from_problem);
  }

  else if (_direction == FROM_MULTIAPP)
  {
    FEProblem & to_problem = _multi_app->problem();
    for (unsigned int i = 0; i < _multi_app->numGlobalApps(); i++)
    if (_multi_app->hasLocalApp(i))
       transfer(to_problem, _multi_app->appProblem(i));
  }

  _console << "Finished LevelSetSolutionTransfer " << name() << std::endl;
}
