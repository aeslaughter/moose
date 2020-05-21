//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html
#pragma once

#include <iostream>
#include "MooseTypes.h"

class ReporterName
{
public:
  ReporterName(const std::string & object_name, const std::string & value_name);
  ReporterName(const ReporterName & other);
  ReporterName & operator=(const ReporterName & other);

  ReporterName() {}
  // friend class InputParameters;

  const std::string & getObjectName() const;
  const std::string & getValueName() const;

  operator std::string() const;
  bool operator==(const ReporterName & rhs) const;

private:
  std::string _object_name;
  std::string _value_name;
  std::string _combined_name;
};

template <>
struct std::hash<ReporterName>
{
  std::size_t operator()(const ReporterName & other) const
  {
    return std::hash<std::string>{}(other);
  }
};

std::ostream & operator<<(std::ostream & os, const ReporterName & state);
