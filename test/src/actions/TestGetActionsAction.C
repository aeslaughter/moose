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

#include "TestGetActionsAction.h"

#include "ActionWarehouse.h"
#include "AddMaterialAction.h"
#include "MooseApp.h"

#include <fstream>

template<>
InputParameters validParams<TestGetActionsAction>()
{
  InputParameters params = validParams<Action>();
  params.addClassDescription("An action demonstrating how an action can interact with other actions");
  params.addParam<FileName>("csv_file", "test_get_actions.csv", "CSV file for printing the action information");
  params.addParam<processor_id_type>("pid", 0, "Test the output on a designated processor, default to master");
  return params;
}

TestGetActionsAction::TestGetActionsAction(const InputParameters & params) :
    Action(params)
{
}

void
TestGetActionsAction::act()
{
  if (_app.processor_id() == getParam<processor_id_type>("pid"))
  {
    // use AddMaterialAction as an example
    auto actions = _awh.getActions<AddMaterialAction>();

    if (actions.size() > 0)
    {
      // to make sure getAction is also working properly
      for (unsigned int i = 0; i < actions.size(); ++i)
      {
        auto action = &_awh.getAction<AddMaterialAction>(actions[i]->name());
        if (actions[i] != action)
          mooseError("something is really wrong");
      }
    }

    std::map<std::string, unsigned int> map_type;
    map_type["GenericConstantMaterial"] = 1;
    map_type["CoupledMaterial"] = 2;
    map_type["RandomMaterial"] = 3;
    map_type["MTMaterial"] = 4;

    std::ofstream os(getParam<FileName>("csv_file").c_str());
    os << "name,name_id,type,type_id" << std::endl;
    for (unsigned int i = 0; i < actions.size(); ++i)
      os << actions[i]->name() << "," << i << ","
         << actions[i]->getMooseObjectType() << "," << map_type[actions[i]->getMooseObjectType()] << std::endl;
    os.close();
  }
}
