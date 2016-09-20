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

#ifndef CFLCONDITION_H
#define CFLCONDITION_H

// MOOSE includes
#include "ElementPostprocessor.h"
#include "LevelSetVelocityInterface.h"

// Forward declarations
class CFLCondition;

template<>
InputParameters validParams<CFLCondition>();

/**
 *
 */
class CFLCondition : public LevelSetVelocityInterface<ElementPostprocessor>
{
public:

  /**
   * Class constructor
   * @param name
   * @param parameters
   */
  CFLCondition(const InputParameters & parameters);

  void initialize(){};

  void execute();
  void finalize();
  void threadJoin(const UserObject & user_object);


  /**
   *
   */
  virtual PostprocessorValue getValue();

private:

  const VariableValue & _velocity_x;
  const VariableValue & _velocity_y;
  const VariableValue & _velocity_z;


  Real _min_width;
  Real _max_velocity;
};

#endif //CFLCONDITION_H
