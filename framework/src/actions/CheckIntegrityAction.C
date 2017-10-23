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

#include "CheckIntegrityAction.h"
#include "ActionWarehouse.h"
#include "FEProblem.h"
#include "BlockRestrictable.h"
#include "Coupleable.h"
#include "MooseVariableInterface.h"

template <>
InputParameters
validParams<CheckIntegrityAction>()
{
  InputParameters params = validParams<Action>();
  return params;
}

CheckIntegrityAction::CheckIntegrityAction(InputParameters params) : Action(params) {}

void
CheckIntegrityAction::act()
{
  _awh.checkUnsatisfiedActions();
  if (_problem.get() != NULL)
    _problem->checkProblemIntegrity();

  for (MooseObject * ptr : _factory.getMooseObjects())
  {
    checkBlocks(ptr);
  }
}

void
CheckIntegrityAction::checkBlocks(MooseObject * moose_object)
{
  BlockRestrictable * blk_ptr = dynamic_cast<BlockRestrictable *>(moose_object);
  if (blk_ptr)
  {
    Coupleable * c_ptr = dynamic_cast<Coupleable *>(moose_object);
    if (c_ptr)
    {
      for (MooseVariable * var : c_ptr->getCoupledMooseVars())
        blk_ptr->checkVariable(*var);
    }

    MooseVariableInterface * mvi_ptr = dynamic_cast<MooseVariableInterface *>(moose_object);
    if (mvi_ptr)
      blk_ptr->checkVariable(*(mvi_ptr->mooseVariable()));
  }
}
