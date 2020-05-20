//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

ReporterStateName::ReporterStateName(const std::string & object_name,
                                     const std::string & value_name)
  : _object_name(object_name),
    _value_name(value_name),
    _combined_name(object_name + "_" + value_name)
{
}

const std::string &
ReporterStateName::getObjectName() const
{
  return _object_name;
}

const std::string &
ReporterStateName::getValueName() const
{
  return _value_name;
}

ReporterStateName::operator std::string() const { return _combined_name; }

bool
ReporterStateName::operator==(const ReporterStateName & rhs) const
{
  return _combined_name == rhs._combined_name;
}

ReporterStateName::ReporterStateName(const ReporterStateName & other)
  : ReporterStateName(other._object_name, other._value_name)
{
}

ReporterStateName &
ReporterStateName::operator=(const ReporterStateName & other)
{
  _object_name = other._object_name;
  _value_name = other._value_name;
  _combined_name = other._combined_name;
  return *this;
}

std::ostream &
operator<<(std::ostream & os, const ReporterStateName & state)
{
  os << state.getObjectName() << "/" << state.getValueName();
  return os;
}

template <>
void
ReporterState<BroadcastValue<Real>>::finalize(const libMesh::Parallel::Communicator & comm)
{
  comm.broadcast(_value.value);
}
