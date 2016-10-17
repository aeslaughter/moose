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

#include "LevelSetProblem.h"
#include "MultiAppTransfer.h"

template<>
InputParameters validParams<LevelSetProblem>()
{
  InputParameters params = validParams<FEProblem>();
  return params;

}

LevelSetProblem::LevelSetProblem(const InputParameters & parameters) :
    FEProblem(parameters)
{
}

void
LevelSetProblem::adaptMesh()
{
  if (!_adaptivity.isAdaptivityDue())
    return;

  unsigned int cycles_per_step = _adaptivity.getCyclesPerStep();
  _cycles_completed = 0;
  for (unsigned int i = 0; i < cycles_per_step; ++i)
  {

    execMultiAppTransfers(EXEC_CUSTOM, MultiAppTransfer::TO_MULTIAPP);

    _console << "Adaptivity step " << i+1 << " of " << cycles_per_step << '\n';
    // Markers were already computed once by Executioner
    if (_adaptivity.getRecomputeMarkersFlag() && i > 0)
      computeMarkers();
    if (_adaptivity.adaptMesh())
    {
      meshChanged();
      _cycles_completed++;
    }
    else
    {
      _console << "Mesh unchanged, skipping remaining steps..." << std::endl;
      return;
    }

    // Show adaptivity progress
    _console << std::flush;
  }
}
