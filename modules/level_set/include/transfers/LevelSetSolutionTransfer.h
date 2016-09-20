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

#ifndef LEVELSETSOLUTIONTRANSFER_H
#define LEVELSETSOLUTIONTRANSFER_H

#include "MultiAppTransfer.h"

// Forward declarations
class LevelSetSolutionTransfer;

template<>
InputParameters validParams<LevelSetSolutionTransfer>();

/**
 * Copy the value to the target domain from the nearest node in the source domain.
 */
class LevelSetSolutionTransfer :
  public MultiAppTransfer
{
public:
  LevelSetSolutionTransfer(const InputParameters & parameters);
  virtual ~LevelSetSolutionTransfer() {}

  virtual void initialSetup();

  virtual void execute();

protected:

  void transfer(FEProblem & to_problem, FEProblem & from_problem);

  const VariableName & _to_var_name;
  const VariableName & _from_var_name;
};

#endif // LEVELSETSOLUTIONTRANSFER_H
