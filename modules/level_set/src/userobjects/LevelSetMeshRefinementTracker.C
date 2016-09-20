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

#include "LevelSetMeshRefinementTracker.h"

// libMesh includes
#include "libmesh/elem.h"

template<>
InputParameters validParams<LevelSetMeshRefinementTracker>()
{
  InputParameters params = validParams<ElementUserObject>();
  return params;
}

LevelSetMeshRefinementTracker::LevelSetMeshRefinementTracker(const InputParameters & parameters) :
    ElementUserObject(parameters)
{
}

void
LevelSetMeshRefinementTracker::execute()
{
  std::cout << _current_elem->id() << " " << _current_elem->refinement_flag() << std::endl;

}


void
LevelSetMeshRefinementTracker::initialize()
{

}

void
LevelSetMeshRefinementTracker::finalize()
{
}

void
LevelSetMeshRefinementTracker::threadJoin(const UserObject & uo)
{

}
