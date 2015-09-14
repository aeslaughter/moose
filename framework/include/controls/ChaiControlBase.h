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

#ifdef LIBMESH_HAVE_CXX11

#ifndef CHAICONTROLBASE_H
#define CHAICONTROLBASE_H

// MOOSE includes
#include "Control.h"

#include <chaiscript/chaiscript.hpp>
#include <chaiscript/chaiscript_stdlib.hpp>

// Forward declarations
class ChaiControlBase;

template<>
InputParameters validParams<ChaiControlBase>();

/**
 *
 */
class ChaiControlBase : public Control
{
public:

  /**
   * Class constructor
   * @param parameters Input parameters for this Control object
   */
  ChaiControlBase(const InputParameters & parameters);

  /**
   * Evaluate the function and set the parameter value
   */
  virtual void execute();

  ///@{
  /**
   * These methods are left intentionally empty
   */
  virtual void initialize(){}
  virtual void finalize(){}
  virtual void threadJoin(const UserObject & /*uo*/){}
  ///@}

protected:

  /// The postprocessor to pass to Python function as a monitor
  const PostprocessorValue & _monitor;

  /// A reference to the parameter to control
  Real & _parameter;


};

#endif // CHAICONTROLBASE_H
#endif // LIBMESH_HAVE_CXX11
