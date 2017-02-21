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

#ifndef TESTADDMATERIALACTION_H
#define TESTADDMATERIALACTION_H

#include "Action.h"

class TestAddMaterialAction;

template<>
InputParameters validParams<TestAddMaterialAction>();

/**
 * Test the action and block restriction work together for materials (see #8575)
 */
class TestAddMaterialAction : public Action
{
public:
  TestAddMaterialAction(const InputParameters & params);
  virtual void act() override;
};

#endif
