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

#ifndef LEVELSETMESHREFINEMENTTRACKER_H
#define LEVELSETMESHREFINEMENTTRACKER_H

// MOOSE includes
#include "ElementUserObject.h"

// Forward Declarations
class LevelSetMeshRefinementTracker;

template<>
InputParameters validParams<LevelSetMeshRefinementTracker>();

class LevelSetMeshRefinementTracker : public ElementUserObject
{
public:
  LevelSetMeshRefinementTracker(const InputParameters & parameters);

protected:

  virtual void execute() override;

  virtual void initialize() override;
  virtual void finalize() override;
  virtual void threadJoin(const UserObject & uo) override;

};

#endif // LEVELSETMESHREFINEMENTTRACKER_H
