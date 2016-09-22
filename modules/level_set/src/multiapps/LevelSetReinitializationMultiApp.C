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

#include "LevelSetReinitializationMultiApp.h"
#include "LevelSetReinitializationProblem.h"

#include "Executioner.h"

// libMesh
#include "libmesh/mesh_tools.h"

template<>
InputParameters validParams<LevelSetReinitializationMultiApp>()
{
  InputParameters params = validParams<MultiApp>();
  params.addParam<unsigned int>("interval", 1, "Time step interval when to perform reinitialization.");

  params.suppressParameter<std::vector<Point> >("positions");
  params.suppressParameter<std::vector<FileName> >("positions_file");
  params.suppressParameter<bool>("output_in_position");
  params.suppressParameter<Real>("reset_time");
  params.suppressParameter<std::vector<unsigned int> >("reset_apps");
  params.suppressParameter<Real>("move_time");
  params.suppressParameter<std::vector<unsigned int> >("move_apps");
  params.suppressParameter<std::vector<Point> >("move_positions");


  return params;
}


LevelSetReinitializationMultiApp::LevelSetReinitializationMultiApp(const InputParameters & parameters):
    MultiApp(parameters),
    _level_set_problem(NULL),
    _interval(getParam<unsigned int>("interval"))
{
}

void
LevelSetReinitializationMultiApp::initialSetup()
{
  MultiApp::initialSetup();

  if (_has_an_app)
  {
    MPI_Comm swapped = Moose::swapLibMeshComm(_my_comm);

    Executioner * ex = _apps[0]->getExecutioner();

    if (!ex)
      mooseError("Executioner does not exist!");

    ex->init();

    _executioner = ex;


    _level_set_problem = dynamic_cast<LevelSetReinitializationProblem *>(&appProblem(0));
    if (!_level_set_problem)
      mooseError("The Problem type must be LevelSetReinitializationProblem.");

      // Swap back
    Moose::swapLibMeshComm(swapped);
  }
}

bool
LevelSetReinitializationMultiApp::solveStep(Real /*dt*/, Real /*target_time*/, bool auto_advance)
{
  // Do nothing if not on interval
  if ((_fe_problem.timeStep() % _interval) != 0)
    return true;

  if (!auto_advance)
    mooseError("LevelSetReinitializationMultiApp is not compatible with auto_advance=false");

  if (!_has_an_app)
    return true;

  MPI_Comm swapped = Moose::swapLibMeshComm(_my_comm);

  _console << "Solving Reinitialization problem." << std::endl;
  Adaptivity & adapt = _level_set_problem->adaptivity();
  adapt.setMarkerVariableName("marker");
  adapt.init(0,0);
  adapt.setUseNewSystem();
  adapt.setMaxHLevel(1);
  _level_set_problem->adaptMesh();

  int rank;
  int ierr;
  ierr = MPI_Comm_rank(_orig_comm, &rank); mooseCheckMPIErr(ierr);

  bool last_solve_converged = true;

  _level_set_problem->resetTime();
  _executioner->execute();
  if (!_executioner->lastSolveConverged())
    last_solve_converged = false;

  // Swap back
  Moose::swapLibMeshComm(swapped);

  return true;//last_solve_converged;
}
