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
#ifndef LEVELSETREINITIALZATIONAPP_H
#define LEVELSETREINITIALZATIONAPP_H

#include "MooseApp.h"

class LevelSetReinitializationApp;

template<>
InputParameters validParams<LevelSetReinitializationApp>();

class LevelSetReinitializationApp : public MooseApp
{
public:
  LevelSetReinitializationApp(const InputParameters & parameters);

  void createMinimalApp() override;

protected:
  virtual void createMeshActions();
  virtual void createVariableActions();
  virtual void createKernelActions();
  virtual void createProblemActions();
  virtual void createUserObjectActions();
  virtual void createExecutionerActions();
  virtual void createOutputActions();



//  MooseSharedPointer<MooseObjectAction> createMooseObjectAction(const std::string & action_name, const std::string & object_name);


  FEProblem * _parent_fep;
  MooseApp & _parent_app;
  ActionWarehouse & _master_awh;

};

#endif /* LEVELSETREINITIALZATIONAPP_H_H */
