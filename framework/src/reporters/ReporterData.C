//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#include "ReporterData.h"
//#include "MooseApp.h"

ReporterData::ReporterData(MooseApp & moose_app):
  _app(moose_app)
{
}


void
ReporterData::init()
{
  for (const std::pair<std::string, std::set<RestartableDataValue *>> & data_pair : _data_ptrs)
    for (auto data_ptr : data_pair.second)
    {
      ReporterContextBase * context_ptr = static_cast<ReporterContextBase *>(data_ptr->context());
      context_ptr->init();
    }


  // assign old/older data
  // shrink_to_fit


  // TODO: Add init_reporter_data action, because FEProblemBase::init is too early
  _initialized = true;
}


void
ReporterData::copyValuesBack()
{
  for (const std::pair<std::string, std::set<RestartableDataValue *>> & data_pair : _data_ptrs)
    for (auto data_ptr : data_pair.second)
    {
      ReporterContextBase * context_ptr = static_cast<ReporterContextBase *>(data_ptr->context());
      context_ptr->copyValuesBack();
    }

}

void
ReporterData::finalize(const std::string & object_name)
{
  // assert
  for (RestartableDataValue * data_ptr : _data_ptrs[object_name])
  {
    ReporterContextBase * context_ptr = static_cast<ReporterContextBase *>(data_ptr->context());
    context_ptr->finalize();
  }
}
