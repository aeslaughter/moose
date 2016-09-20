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
#include "LevelSetMeshRefinementTransfer.h"
//#include "MooseTypes.h"
#include "FEProblem.h"
//#include "DisplacedProblem.h"
#include "MultiApp.h"
#include "MooseMesh.h"
//#include "NonlinearSystem.h"

// libMesh includes
//#include "libmesh/system.h"
//#include "libmesh/mesh_tools.h"
//#include "libmesh/id_types.h"

template<>
InputParameters validParams<LevelSetMeshRefinementTransfer>()
{
  InputParameters params = validParams<MultiAppTransfer>();
  return params;
}

LevelSetMeshRefinementTransfer::LevelSetMeshRefinementTransfer(const InputParameters & parameters) :
    MultiAppTransfer(parameters)
{
}

void
LevelSetMeshRefinementTransfer::transfer(FEProblem & to_problem, FEProblem & from_problem)
{
  MPI_Comm swapped = Moose::swapLibMeshComm(_multi_app->comm());

  MeshBase * to_mesh = &to_problem.mesh().getMesh();
  MeshBase * from_mesh = &from_problem.mesh().getMesh();

  MeshBase::const_element_iterator to_elem_it = to_mesh->local_elements_begin();
  MeshBase::const_element_iterator to_elem_end = to_mesh->local_elements_end();

  for (; to_elem_it != to_elem_end; ++to_elem_it)
  {
    Elem * to_elem = *to_elem_it;
    Elem * from_elem = from_mesh->elem_ptr(to_elem->id());

    Elem::RefinementState from_state = from_elem->refinement_flag();
    Elem::RefinementState to_state = to_elem->refinement_flag();

    
    /*
    if (from_state == Elem::RefinementState::INACTIVE)
      to_elem->set_refinement_flag(Elem::RefinementState::REFINE);
    if (to_state == Elem::RefinementState::INACTIVE)
      to_elem->set_refinement_flag(Elem::RefinementState::COARSEN);
    */

    // Displaced problem
  }

  MeshRefinement mesh_refinement(*to_mesh);
  bool mesh_changed = mesh_refinement.refine_and_coarsen_elements();
  if (mesh_changed)
  {
    to_problem.mesh().meshChanged();
    to_problem.meshChanged();
    //_console << "\nMesh Changed:\n";
    // to_problem.mesh().printInfo();
  }
  // Swap back
  Moose::swapLibMeshComm(swapped);
}

void
LevelSetMeshRefinementTransfer::execute()
{
  _console << "Beginning LevelSetMeshRefinementTransfer " << name() << std::endl;

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

  _console << "Finished LevelSetMeshRefinementTransfer " << name() << std::endl;
}
