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

#include "MultiAppVectorPostprocessorTransfer.h"

// MOOSE includes
#include "MooseTypes.h"
#include "FEProblem.h"
#include "MultiApp.h"

// libMesh
#include "libmesh/meshfree_interpolation.h"
#include "libmesh/system.h"

template<>
InputParameters validParams<MultiAppVectorPostprocessorTransfer>()
{
  InputParameters params = validParams<MultiAppTransfer>();



  params.addRequiredParam<VectorPostprocessorName>("vector_postprocessor", "The name of the VectorPostprocessor in the Master to transfer the value to/from.");
  params.addRequiredParam<std::string>("vector_postprocessor_vector_name", "The name of the vector within the vector postprocessor being transferred to/from.");

  params.addRequiredParam<PostprocessorName>("postprocessor", "The name of the Postprocessor in the MultiApp to transfer the value to/from.");

  return params;
}

MultiAppVectorPostprocessorTransfer::MultiAppVectorPostprocessorTransfer(const InputParameters & parameters) :
    MultiAppTransfer(parameters),
    _pp_name(getParam<PostprocessorName>("postprocessor")),
    _vector_pp_name(getParam<VectorPostprocessorName>("vector_postprocessor")),
    _vector_pp_vector_name(getParam<std::string>("vector_postprocessor_vector_name"))
{
}

void
MultiAppVectorPostprocessorTransfer::transfer(FEProblem & master_problem, FEProblem & sub_problem, unsigned int app_num)
{
  VectorPostprocessorValue & vector_pp = master_problem.getVectorPostprocessorValue(_vector_pp_name, _vector_pp_vector_name);
  PostprocessorValue & pp = sub_problem.getPostprocessorValue(_pp_name);

  if (_direction == TO_MULTIAPP)
    pp = vector_pp[app_num];

  else if (_direction == FROM_MULTIAPP)
    vector_pp[app_num] = pp;

}


void
MultiAppVectorPostprocessorTransfer::execute()
{


  _console << "Beginning PostprocessorToVectorPostprocessorTransfer " << name() << std::endl;

  FEProblem & master_problem = _multi_app->problem();
  for (unsigned int i = 0; i < _multi_app->numGlobalApps(); i++)
    if (_multi_app->hasLocalApp(i))
      transfer(master_problem, _multi_app->appProblem(i) ,i);

  _console << "Finished PostprocessorToVectorPostprocessorTransfer " << name() << std::endl;
}
