//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#pragma once

#include "LineSegmentCutSetUserObject.h"
#include "XFEMMovingInterfaceVelocityBase.h"

// Forward declarations
class PointValueAtXFEMInterface;

class MovingLineSegmentCutSetUserObject : public LineSegmentCutSetUserObject

{
public:
  static InputParameters validParams();

  MovingLineSegmentCutSetUserObject(const InputParameters & parameters);

  virtual void initialize() override;

  virtual void execute() override;

  virtual void finalize() override;

  virtual const std::vector<Point>
  getCrackFrontPoints(unsigned int num_crack_front_points) const override;

  virtual Real cutFraction(unsigned int cut_num, Real time) const override;

  virtual GeometricCutSubdomainID getGeometricCutSubdomainID(const Node * node) const override;

protected:
  /// Calculate the signed distance function at a point
  virtual Real calculateSignedDistance(Point p) const;

  /// Pointer to XFEMMovingInterfaceVelocityBase object
  const XFEMMovingInterfaceVelocityBase * _interface_velocity;

  /// The GeometricCutSubdomainID for the negative side of the cut
  const GeometricCutSubdomainID _negative_id;

  /// The GeometricCutSubdomainID for the positive side of the cut
  const GeometricCutSubdomainID _positive_id;
};
