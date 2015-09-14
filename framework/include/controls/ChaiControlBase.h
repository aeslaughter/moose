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


#ifndef CHAICONTROLBASE_H
#define CHAICONTROLBASE_H

// MOOSE includes
#include "Control.h"

// ChaiScript requires Cxx11
#ifdef LIBMESH_HAVE_CXX11

// ChaiScript includes
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

  void test();
  double value;

protected:

  /// The postprocessor to pass to Python function as a monitor
  //const PostprocessorValue & _monitor;

  /// A reference to the parameter to control
//  Real & _parameter;


};

#endif // LIBMESH_HAVE_CXX11
#endif // CHAICONTROLBASE_H
