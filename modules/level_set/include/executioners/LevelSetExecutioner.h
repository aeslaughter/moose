#ifndef LEVELSETEXECUTIONER_H
#define LEVELSETEXECUTIONER_H

#include "Transient.h"

class LevelSetExecutioner;

template<>
InputParameters validParams<LevelSetExecutioner>();

class LevelSetExecutioner: public Transient
{
public:
  LevelSetExecutioner(const InputParameters & parameters);

  virtual void postStep() override;

};

#endif // LEVELSETEXECUTIONER_H
