//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#include "ReporterData.h"
#include "MooseApp.h"

ReporterData::ReporterData(MooseApp & moose_app),
  _app(moose_app)
{
}


void
ReporterData::init()
{
  // assign old/older data
  // shrink_to_fit

  _initialized = true;
}


void
ReporterData::finalize(const std::string & object_name)
{
  /*
  for (std::pair<const ReporterName, std::unique_ptr<ReporterStateBase>> & pair :
         _reporter_states)
    if (pair.first.getObjectName() == object_name)
      pair.second->finalize(comm());
  */
}
