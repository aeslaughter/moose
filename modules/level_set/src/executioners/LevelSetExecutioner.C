#include "LevelSetExecutioner.h"

template<>
InputParameters validParams<LevelSetExecutioner>()
{
  InputParameters params = validParams<Transient>();
  return params;
}

LevelSetExecutioner::LevelSetExecutioner(const InputParameters & parameters) :
    Transient(parameters)
{
}

void
LevelSetExecutioner::postStep()
{
  //std::cout << "LevelSetExecutioner::postStep" << std::endl;
  //_fe_problem.execMultiApps(EXEC_CUSTOM);
}
