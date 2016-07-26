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
#include "SolutionL2Norm.h"
#include "NonlinearSystem.h"

template<>
InputParameters validParams<SolutionL2Norm>()
{
  InputParameters params = validParams<GeneralPostprocessor>();
  return params;
}

SolutionL2Norm::SolutionL2Norm(const InputParameters & parameters) :
    GeneralPostprocessor(parameters)
{}

PostprocessorValue
SolutionL2Norm::getValue()
{
  return _fe_problem.getNonlinearSystem().currentSolution()->l2_norm();
}
