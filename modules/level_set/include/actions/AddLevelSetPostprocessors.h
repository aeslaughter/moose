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

#ifndef ADDLEVELSETPOSTPROCESSORS_H
#define ADDLEVELSETPOSTPROCESSORS_H

// LevelSet includes
#include "LevelSetActionBase.h"

// Forward declarations
class AddLevelSetPostprocessors;

template<>
InputParameters validParams<AddLevelSetPostprocessors>();

/**
 * Action for automatically adding level set related postprocessors.
 */
class AddLevelSetPostprocessors : public LevelSetActionBase
{
public:
  AddLevelSetPostprocessors(InputParameters parameters);

  /**
   * Adds the optional level set postprocessors.
   */
  virtual void act();
};

#endif // ADDLEVELSETPOSTPROCESSORS_H
