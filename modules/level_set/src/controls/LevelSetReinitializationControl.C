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
#include "LevelSetReinitializationControl.h"
#include "NonlinearSystem.h"
#include "Transient.h"

template<>
InputParameters validParams<LevelSetReinitializationControl>()
{
  InputParameters params = validParams<Control>();
  params.addRequiredParam<Real>("tol", "The limit at which the reinitialization problem is considered converged.");
  params.addParam<unsigned int>("min_steps", 3, "The minimum number of time steps to consider.");
  return params;
}


LevelSetReinitializationControl::LevelSetReinitializationControl(const InputParameters & parameters) :
    Control(parameters),
    _solution_diff(_fe_problem.getNonlinearSystem().addVector("solution_diff", false, PARALLEL)),
    _on_reinit(false),
    _current_time(_fe_problem.time()),
    _tol(getParam<Real>("tol")),
    _min_t_steps(getParam<unsigned int>("min_steps")),
    _main_name(_app.name())
{
}


void
LevelSetReinitializationControl::execute()
{

  if (!_on_reinit)
  {
    setControllableValueByName<bool>(std::string("levelset::advection"), std::string("enable"),  false);
    setControllableValueByName<bool>(std::string("levelset::out"), std::string("enable"),  false);
    setControllableValueByName<bool>(std::string("reinit::olsson"), std::string("enable"),  true);
    _current_time = _executioner->getTime();
    _executioner->setTime(0.0);
    _executioner->setTimeOld(0.0);
    _on_reinit = true;
    _reinit_t_steps = 0;
    _app.setUseNamePrefix(true);
    _app.setName(std::string("Reinitialization:") + _main_name);
  }

  else
  {
    _solution_diff  = *_fe_problem.getNonlinearSystem().currentSolution();
    _solution_diff -= _fe_problem.getNonlinearSystem().solutionOld();
    Real delta = _solution_diff.l2_norm() / _dt;
    _console << "Computed convergence criteria: " << delta << std::endl;
    _reinit_t_steps++;

    if (delta < _tol && _reinit_t_steps > _min_t_steps)
    {
      _executioner->setTimeOld(_current_time);
      setControllableValueByName<bool>(std::string("levelset::advection"), std::string("enable"),  true);
      setControllableValueByName<bool>(std::string("levelset::out"), std::string("enable"),  true);
      setControllableValueByName<bool>(std::string("reinit::olsson"), std::string("enable"),  false);
      _on_reinit = false;
      _app.setUseNamePrefix(false);
      _app.setName(_main_name);
    }
  }

}


void
LevelSetReinitializationControl::initialSetup()
{

  _executioner = MooseSharedNamespace::dynamic_pointer_cast<Transient>(_app.executioner());

/*
  std::multimap<MooseObjectName, MooseSharedPointer<InputParameters> >::iterator iter;
  for (iter = _input_parameter_warehouse.begin(0); iter != _input_parameter_warehouse.end(0); ++iter)
  {
    std::cout << iter->first << std::endl;
  }
*/
}
