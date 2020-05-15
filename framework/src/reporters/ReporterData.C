//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#include "ReporterData.h"
#include "FEProblemBase.h"

ReporterData::ReporterData(FEProblemBase & fe_problem)
  : Restartable(fe_problem.getMooseApp(), "values", "ReporterData", 0), ParallelObject(fe_problem)
{
}
