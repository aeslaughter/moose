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

#ifndef LEVELSETVELOCITYINTERFACE_H
#define LEVELSETVELOCITYINTERFACE_H

// MOOSE includes
#include "InputParameters.h"
#include "MooseVariableBase.h"
#include "Kernel.h"

template<typename T = Kernel>
class LevelSetVelocityInterface;

//void injectLevelSetVelocityInterfaceParameters(InputParameters & parameters);
template<>
InputParameters validParams<LevelSetVelocityInterface<> >();

/**
 * A helper class for defining the velocity as coupled variables
 * for the levelset equation.
 */
template<class T>
class LevelSetVelocityInterface : public T
{
public:
  LevelSetVelocityInterface(const InputParameters & parameters);

protected:

  void computeQpVelocity();

  ///@{
  /// Coupled velocity variables
  const VariableValue & _velocity_x;
  const VariableValue & _velocity_y;
  const VariableValue & _velocity_z;
  ///@}

  ///@{
  /// Coupled velocity identifiers
  const unsigned int _x_vel_var;
  const unsigned int _y_vel_var;
  const unsigned int _z_vel_var;
  ///@}

  /// Storage for velocity vector
  RealVectorValue _velocity;
};


template<class T>
void
LevelSetVelocityInterface<T>::computeQpVelocity()
{
  _velocity(0) = _velocity_x[T::_qp];
  _velocity(1) = _velocity_y[T::_qp];
  _velocity(2) = _velocity_z[T::_qp];
}

template<class T>
LevelSetVelocityInterface<T>::LevelSetVelocityInterface(const InputParameters & parameters) :
    T(parameters),
    _velocity_x(T::coupledValue("velocity_x")),
    _velocity_y(T::coupledValue("velocity_y")),
    _velocity_z(T::coupledValue("velocity_z")),
    _x_vel_var(T::coupled("velocity_x")),
    _y_vel_var(T::coupled("velocity_y")),
    _z_vel_var(T::coupled("velocity_z"))
{
}

#endif // LEVELSETVELOCITYINTERFACE_H
