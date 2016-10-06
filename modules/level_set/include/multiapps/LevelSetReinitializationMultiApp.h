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
#ifndef LEVELSETREINITIALIZATIONMULTIAPP_H
#define LEVELSETREINITIALIZATIONMULTIAPP_H

#include "MultiApp.h"

// Forward declarations
class LevelSetReinitializationMultiApp;
class LevelSetReinitializationProblem;
class Executioner;

template<>
InputParameters validParams<LevelSetReinitializationMultiApp>();

void add_reinitialization_param(InputParameters & params);

class LevelSetReinitializationMultiApp : public MultiApp
{
public:
  LevelSetReinitializationMultiApp(const InputParameters & parameters);


  virtual void initialSetup() override;

  /**
   * Completely solve all of the Apps
   */
  virtual bool solveStep(Real dt, Real target_time, bool auto_advance=true) override;

  /**
   * Actually advances time and causes output.
   */
  virtual void advanceStep() override {}

protected:

  void createAppSetup(unsigned int i, InputParameters & app_params) override;

  LevelSetReinitializationProblem * _level_set_problem;

  Executioner * _executioner;

  const unsigned int & _interval;
};

#endif // LevelSetReinitializationMultiApp_H
