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

#ifndef LEVELSETOLSSONTERMINATOR_H
#define LEVELSETOLSSONTERMINATOR_H

#include "GeneralUserObject.h"

//Forward Declarations
class LevelSetOlssonTerminator;
class Transient;

template<>
InputParameters validParams<LevelSetOlssonTerminator>();

/**
 * Gets the relative solution norm from the transient executioner
 */
class LevelSetOlssonTerminator : public GeneralUserObject
{
public:
  /**
   * Class constructor
   * @param parameters The input parameters
   */
  LevelSetOlssonTerminator(const InputParameters & parameters);

  /**
   * Checks the steady-state convergence criteria of Olsson.
   */
  virtual void execute() override;


  ///@{
  /**
   * No action taken
   */
   virtual void initialize() override {}
   virtual void finalize() override {}
  ///@}

protected:

  /// The difference of current and old solutions
  NumericVector<Number> & _solution_diff;

  /// The steady-state convergence tolerance
  const Real & _tol;

  /// The required minimum number of timesteps
  const int & _min_t_steps;

};

#endif //LEVELSETOLSSONTERMINATOR_H
