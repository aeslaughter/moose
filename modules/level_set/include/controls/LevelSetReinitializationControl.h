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

#ifndef LEVELSETREINITIALIZATIONCONTROL_H
#define LEVELSETREINITIALIZATIONCONTROL_H

// MOOSE includes
#include "Control.h"

// Forward declarations
class LevelSetReinitializationControl;
class Transient;

template<>
InputParameters validParams<LevelSetReinitializationControl>();

class LevelSetReinitializationControl : public Control
{
public:

  LevelSetReinitializationControl(const InputParameters & parameters);

  virtual void execute() override;

protected:

  /**
   * If enabled, this injects the start/end times into the TimeStepper sync times.
   */
  void initialSetup() override;

    /// The difference of current and old solutions
  NumericVector<Number> & _solution_diff;

  bool _on_reinit;

  Real _current_time;

    /// The steady-state convergence tolerance
  const Real & _tol;

  /// The required minimum number of timesteps
  const unsigned int & _min_t_steps;

  unsigned int _reinit_t_steps = 0;

  const std::string _main_name;

  MooseSharedPointer<Transient> _executioner;

};

#endif // LEVELSETREINITIALIZATIONCONTROL_H
