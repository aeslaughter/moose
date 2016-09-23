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

#include "LevelSetReinitializationProblem.h"

template<>
InputParameters validParams<LevelSetReinitializationProblem>()
{
  InputParameters params = validParams<FEProblem>();
  params.addParam<Real>("steady_state_tol", 1e-8, "The relative difference between the new solution and the old solution that will be considered to be at steady state");
  return params;

}

LevelSetReinitializationProblem::LevelSetReinitializationProblem(const InputParameters & parameters) :
    FEProblem(parameters),
    _steady_state_tol(getParam<Real>("steady_state_tol"))
{
}


void
LevelSetReinitializationProblem::resetTime()
{
  _time = 0.0;
  _time_old = 0.0;
  _t_step = 0;
  _termination_requested = false;
}
