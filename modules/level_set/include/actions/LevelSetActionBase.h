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

#ifndef LEVELSETACTIONBASE_H
#define LEVELSETACTIONBASE_H

// MOOSE includes
#include "Action.h"
#include "LevelSetVelocityInterface.h"

// Forward declarations
class LevelSetActionBase;

template<>
InputParameters validParams<LevelSetActionBase>();

/**
 * Base for creating actions for the level set equation.
 */
class LevelSetActionBase : public Action
{
public:
  LevelSetActionBase(InputParameters parameters);

protected:

  /// The name of the levelset variable.
  const NonlinearVariableName & _variable_name;

  /**
   * Helper methods for inserting the level set variable name into an InputParameter object.
   * @param params The input parameters to apply variable name.
   */
  void injectVariableParam(InputParameters & params);

  /**
   * Helper method for inserting the velocity variable names into an InputParameter object.
   * @param params The input parameters to apply velocity coupled parameters.
   */
  void injectVelocityParams(InputParameters & params);
};

#endif // LEVELSETACTIONBASE_H
