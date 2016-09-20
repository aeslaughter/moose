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

#ifndef ADDLEVELSETKERNELS_H
#define ADDLEVELSETKERNELS_H

// LevelSet includes
#include "LevelSetActionBase.h"

// Forward declarations
class AddLevelSetKernels;

template<>
InputParameters validParams<AddLevelSetKernels>();

/**
 * Action for automatically adding the required and optional kernels
 * MOOSE objects for computing the level set equation.
 */
class AddLevelSetKernels : public LevelSetActionBase
{
public:
  AddLevelSetKernels(InputParameters parameters);

  /**
   * Adds the required Kernels to formulate the basic level set equation.
   *
   * \frac{\partial\phi}{\partial t} + \vec{v} \cdot \nabal\phi = 0
   */
  virtual void act();

  /**
   * Adds level set related postprocessors, if desired.
   */
  //void addLevelSetPostprocessors();

};

#endif // ADDLEVELSETKERNELS_H
