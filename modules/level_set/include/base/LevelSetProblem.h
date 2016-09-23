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

#include "FEProblem.h"

class LevelSetProblem;

template<>
InputParameters validParams<LevelSetProblem>();

class LevelSetProblem : public FEProblem
{
public:
  LevelSetProblem(const InputParameters & parameters);

  virtual void computeMarkers() override;
  virtual void adaptMesh() override;

};
