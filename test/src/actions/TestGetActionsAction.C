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

  // A switch for changing the function that is being tested
  MooseEnum test_function("getAction getActions");
  params.addRequiredParam<MooseEnum>("test_function", test_function, "The function to test: getActions or getAction.");

  return params;
}

TestGetActionsAction::TestGetActionsAction(const InputParameters & params) :
    Action(params),
    _test_function(getParam<MooseEnum>("test_function"))
{
}

void
TestGetActionsAction::act()
{
  if (_app.processor_id() == getParam<processor_id_type>("pid"))
  {
    // use AddMaterialAction as an example
    auto actions = _awh.getActions<AddMaterialAction>();

    // Test to make sure "getAction" is also working properly
    if (_test_function == "getAction")
      for (unsigned int i = 0; i < actions.size(); ++i)
      {
        auto action = &_awh.getAction<AddMaterialAction>(actions[i]->name());
        if (actions[i] != action)
          mooseError("getAction is returning the wrong type, something is really wrong!");
      }

    // Test the "getActions" function
    else if (_test_function == "getActions")
    {
      std::ofstream os(getParam<FileName>("csv_file").c_str());
      os << "name,name_id,type" << std::endl;
      for (unsigned int i = 0; i < actions.size(); ++i)
        os << actions[i]->name() << "," << i << "," << actions[i]->getMooseObjectType() << std::endl;
      os.close();
    }

    // Error if the test type was not set, this shouldn't be possible
    else
      mooseError("Invalid test type, you must select 'getAction' or 'getActions'. How did you do this?");
  }
}
