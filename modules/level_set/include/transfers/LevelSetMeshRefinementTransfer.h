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

#ifndef LEVELSETMESHREFINEMENTTRANSFER_H
#define LEVELSETMESHREFINEMENTTRANSFER_H

#include "MultiAppTransfer.h"

// Forward declarations
class LevelSetMeshRefinementTransfer;

template<>
InputParameters validParams<LevelSetMeshRefinementTransfer>();

/**
 * Copy the value to the target domain from the nearest node in the source domain.
 */
class LevelSetMeshRefinementTransfer : public MultiAppTransfer
{
public:
  LevelSetMeshRefinementTransfer(const InputParameters & parameters);

  virtual void execute() override;

protected:

  void transfer(FEProblem & to_problem, FEProblem & from_problem);
};

#endif // LEVELSETMESHREFINEMENTTRANSFER_H
