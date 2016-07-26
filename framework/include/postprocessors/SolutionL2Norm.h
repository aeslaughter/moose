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

#ifndef SOLUTIONL2NORM_H
#define SOLUTIONL2NORM_H

// MOOSE includes
#include "GeneralPostprocessor.h"

// Forward Declarations
class SolutionL2Norm;

template<>
InputParameters validParams<SolutionL2Norm>();

/**
 * The L2 norm of the complete solution vector (i.e., all variables).
 */
class SolutionL2Norm :
    public GeneralPostprocessor
{
public:
  SolutionL2Norm(const InputParameters & parameters);

  /**
   * Returns the L2 norm for the complete solution vector.
   */
  virtual PostprocessorValue getValue() override;

  ///@{
  /**
   * These methods left intentionally empty.
   */
  virtual void initialize() override {};
  virtual void execute() override {};
  ///@}

};

#endif // SOLUTIONL2NORM_H
