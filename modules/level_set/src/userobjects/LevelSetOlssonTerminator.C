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

#include "LevelSetOlssonTerminator.h"
#include "NonlinearSystem.h"

template<>
InputParameters validParams<LevelSetOlssonTerminator>()
{
  InputParameters params = validParams<GeneralUserObject>();
  params.addRequiredParam<Real>("tol", "The limit at which the reinitialization problem is considered converged.");
  params.addParam<int>("min_steps", 3, "The minimum number of time steps to consider.");
  return params;
}

LevelSetOlssonTerminator::LevelSetOlssonTerminator(const InputParameters & params) :
    GeneralUserObject(params),
    _solution_diff(_fe_problem.getNonlinearSystem().addVector("solution_diff", false, PARALLEL)),
    _tol(getParam<Real>("tol")),
    _min_t_steps(getParam<int>("min_steps"))
{
}

void
LevelSetOlssonTerminator::execute()
{
  if (_fe_problem.timeStep() < _min_t_steps)
    return;

  _solution_diff  = *_fe_problem.getNonlinearSystem().currentSolution();
  _solution_diff -= _fe_problem.getNonlinearSystem().solutionOld();
  Real delta = _solution_diff.l2_norm() / _dt;
  _console << "Computed convergence criteria: " << delta << std::endl;

  if (delta < _tol )
    _fe_problem.terminateSolve();

}
