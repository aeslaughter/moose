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
  : _combined_name(object_name + "_" + value_name)
{
}

ReporterStateName::operator std::string() const { return _combined_name; }

bool
ReporterStateName::operator==(const ReporterStateName & rhs) const
{
  return _combined_name == rhs._combined_name;
}
