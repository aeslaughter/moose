//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#include "VectorPostprocessorInterface.h"
#include "FEProblem.h"
#include "VectorPostprocessor.h"
#include "MooseTypes.h"

VectorPostprocessorInterface::VectorPostprocessorInterface(const MooseObject * moose_object,
                                                           bool broadcast_by_default)
  : _broadcast_by_default(broadcast_by_default),
    _vpi_params(moose_object->parameters()),
    _vpi_feproblem(*_vpi_params.getCheckedPointerParam<FEProblemBase *>("_fe_problem_base")),
    _vpi_tid(_vpi_params.have_parameter<THREAD_ID>("_tid") ? _vpi_params.get<THREAD_ID>("_tid")
                                                           : 0),
    _vpi_reporter_data(_vpi_feproblem.getReporterData())
{
}

const VectorPostprocessorValue &
VectorPostprocessorInterface::getVectorPostprocessorValue(const std::string & name,
                                                          const std::string & vector_name)
{
  return getVectorPostprocessorValueByName(_vpi_params.get<VectorPostprocessorName>(name),
                                           vector_name);
}

const VectorPostprocessorValue &
VectorPostprocessorInterface::getVectorPostprocessorValueByName(
    const VectorPostprocessorName & name, const std::string & vector_name)
{
  return getVectorPostprocessorByNameHelper(name, vector_name, _broadcast_by_default, 0);
}

const VectorPostprocessorValue &
VectorPostprocessorInterface::getVectorPostprocessorValueOld(const std::string & name,
                                                             const std::string & vector_name)
{
  return getVectorPostprocessorValueOldByName(_vpi_params.get<VectorPostprocessorName>(name),
                                              vector_name);
}

const VectorPostprocessorValue &
VectorPostprocessorInterface::getVectorPostprocessorValueOldByName(
    const VectorPostprocessorName & name, const std::string & vector_name)
{
  return getVectorPostprocessorByNameHelper(name, vector_name, _broadcast_by_default, 1);
}

const VectorPostprocessorValue &
VectorPostprocessorInterface::getVectorPostprocessorValue(const std::string & name,
                                                          const std::string & vector_name,
                                                          bool needs_broadcast)
{
  return getVectorPostprocessorValueByName(
      _vpi_params.get<VectorPostprocessorName>(name), vector_name, needs_broadcast);
}

const VectorPostprocessorValue &
VectorPostprocessorInterface::getVectorPostprocessorValueByName(
    const VectorPostprocessorName & name, const std::string & vector_name, bool needs_broadcast)
{
  return getVectorPostprocessorByNameHelper(
      name, vector_name, needs_broadcast || _broadcast_by_default, 0);
}

const VectorPostprocessorValue &
VectorPostprocessorInterface::getVectorPostprocessorValueOld(const std::string & name,
                                                             const std::string & vector_name,
                                                             bool needs_broadcast)
{
  return getVectorPostprocessorValueOldByName(
      _vpi_params.get<VectorPostprocessorName>(name), vector_name, needs_broadcast);
}

const VectorPostprocessorValue &
VectorPostprocessorInterface::getVectorPostprocessorValueOldByName(
    const VectorPostprocessorName & name, const std::string & vector_name, bool needs_broadcast)
{
  return getVectorPostprocessorByNameHelper(
      name, vector_name, needs_broadcast || _broadcast_by_default, 1);
}

const ScatterVectorPostprocessorValue &
VectorPostprocessorInterface::getScatterVectorPostprocessorValue(const std::string & name,
                                                                 const std::string & vector_name)
{
  return _vpi_feproblem.getScatterVectorPostprocessorValue(
      _vpi_params.get<VectorPostprocessorName>(name), vector_name);
}

const ScatterVectorPostprocessorValue &
VectorPostprocessorInterface::getScatterVectorPostprocessorValueByName(
    const std::string & name, const std::string & vector_name)
{
  return _vpi_feproblem.getScatterVectorPostprocessorValue(name, vector_name);
}

const ScatterVectorPostprocessorValue &
VectorPostprocessorInterface::getScatterVectorPostprocessorValueOld(const std::string & name,
                                                                    const std::string & vector_name)
{
  return _vpi_feproblem.getScatterVectorPostprocessorValueOld(
      _vpi_params.get<VectorPostprocessorName>(name), vector_name);
}

const ScatterVectorPostprocessorValue &
VectorPostprocessorInterface::getScatterVectorPostprocessorValueOldByName(
    const std::string & name, const std::string & vector_name)
{
  return _vpi_feproblem.getScatterVectorPostprocessorValueOld(name, vector_name);
}

bool
VectorPostprocessorInterface::hasVectorPostprocessor(const std::string & name) const
{
  return _vpi_feproblem.hasVectorPostprocessor(_vpi_params.get<VectorPostprocessorName>(name));
}

bool
VectorPostprocessorInterface::hasVectorPostprocessorByName(
    const VectorPostprocessorName & name) const
{
  return _vpi_feproblem.hasVectorPostprocessor(name);
}

bool
VectorPostprocessorInterface::isVectorPostprocessorDistributed(const std::string & name) const
{
  const VectorPostprocessorData & data = _vpi_feproblem.getVectorPostprocessorData();
  return data.isDistributed(_vpi_params.get<VectorPostprocessorName>(name));
}

bool
VectorPostprocessorInterface::isVectorPostprocessorDistributedByName(
    const VectorPostprocessorName & name) const
{
  const VectorPostprocessorData & data = _vpi_feproblem.getVectorPostprocessorData();
  return data.isDistributed(name);
}

const VectorPostprocessorValue &
VectorPostprocessorInterface::getVectorPostprocessorByNameHelper(const std::string & object_name,
                                                                 const std::string & vector_name,
                                                                 bool broadcast,
                                                                 std::size_t t_index) const
{
  Moose::ReporterMode mode =
      broadcast ? Moose::ReporterMode::REPLICATED : Moose::ReporterMode::ROOT;
  ReporterName r_name(object_name, vector_name);
  return _vpi_reporter_data.getReporterValue<VectorPostprocessorValue>(
      r_name, object_name, mode, t_index);
}
