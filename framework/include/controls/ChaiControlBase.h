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

// Forward declarations
template<typename T = Real>
class ChaiControlBase;

template<>
InputParameters validParams<ChaiControlBase<> >();

/**
 * A base class for controlling MOOSE via python functions
 *
 * By default a function with the name 'function' that resides
 * in a module with the name 'control.py' located in the working directory
 * is called.
 *
 * This class has two methods that must be defined in the child class:
 * buildPythonArguments and getPythonResult.
 *
 * @see RealChaiControl
 */
template<typename T>
class ChaiControlBase : public Control
{
public:

  /**
   * Class constructor
   * @param parameters Input parameters for this Control object
   */
  ChaiControlBase(const InputParameters & parameters);

  /**
   * Class destructor
   */
  virtual ~ChaiControlBase();
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
  T & _parameter;


};

template<typename T>
ChaiControlBase<T>::ChaiControlBase(const InputParameters & parameters) :
    Control(parameters),
    _monitor(getPostprocessorValue("monitor")),
    _parameter(getControllableParam<Real>("parameter"))
{
}

template<typename T>
ChaiControlBase<T>::~ChaiControlBase()
{
}

template<typename T>
void
ChaiControlBase<T>::execute()
{

}

#endif // CHAICONTROLBASE_H
#endif // LIBMESH_HAVE_CXX11
