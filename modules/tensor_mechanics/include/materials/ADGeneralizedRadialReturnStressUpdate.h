//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#pragma once

#include "ADStressUpdateBase.h"
#include "ADGeneralizedReturnMappingSolution.h"

/**
 * ADRadialReturnStressUpdate computes the radial return stress increment for
 * an isotropic elastic-viscoplasticity model after interating on the difference
 * between new and old trial stress increments.  This radial return mapping class
 * acts as a base class for the radial return creep and plasticity classes / combinations.
 * The stress increment computed by ADRadialReturnStressUpdate is used by
 * ComputeMultipleInelasticStress which computes the elastic stress for finite
 * strains.  This return mapping class is acceptable for finite strains but not
 * total strains.
 * This class is based on the Elasto-viscoplasticity algorithm in F. Dunne and N.
 * Petrinic's Introduction to Computational Plasticity (2004) Oxford University Press.
 */

#include "ADReal.h"

#include <Eigen/Core>
#include <Eigen/Eigenvalues>

namespace Eigen
{
namespace internal
{
template <>
struct cast_impl<ADReal, int>
{
  static inline int run(const ADReal & x) { return static_cast<int>(MetaPhysicL::raw_value(x)); }
};
} // namespace internal
} // namespace Eigen
typedef Eigen::Matrix<ADReal, 6, 6, Eigen::DontAlign> AnisotropyMatrix;

class ADGeneralizedRadialReturnStressUpdate : public ADStressUpdateBase,
                                              public ADGeneralizedReturnMappingSolution
{
public:
  static InputParameters validParams();

  ADGeneralizedRadialReturnStressUpdate(const InputParameters & parameters);

  /**
   * A radial return (J2) mapping method is performed with return mapping
   * iterations.
   * @param strain_increment              Sum of elastic and inelastic strain increments
   * @param inelastic_strain_increment    Inelastic strain increment calculated by this class
   * @param rotation increment            Not used by this class
   * @param stress_new                    New trial stress from pure elastic calculation
   * @param stress_old                    Old state of stress
   * @param elasticity_tensor             Rank 4 C_{ijkl}, must be isotropic
   * @param elastic_strain_old            Old state of total elastic strain
   */
  virtual void updateState(ADRankTwoTensor & strain_increment,
                           ADRankTwoTensor & inelastic_strain_increment,
                           const ADRankTwoTensor & rotation_increment,
                           ADRankTwoTensor & stress_new,
                           const RankTwoTensor & stress_old,
                           const ADRankFourTensor & elasticity_tensor,
                           const RankTwoTensor & elastic_strain_old) override;

  virtual Real computeReferenceResidual(const ADDenseVector & effective_trial_stress,
                                        const ADDenseVector & stress_new,
                                        const ADReal & residual,
                                        const ADReal & scalar_effective_inelastic_strain) override;

  virtual ADReal
  minimumPermissibleValue(const ADDenseVector & /*effective_trial_stress*/) const override
  {
    return 0.0;
  }

  virtual ADReal
  maximumPermissibleValue(const ADDenseVector & effective_trial_stress) const override;

  /**
   * Compute the limiting value of the time step for this material
   * @return Limiting time step
   */
  virtual Real computeTimeStepLimit() override;

  /**
   * Does the model require the elasticity tensor to be isotropic?
   */
  bool requiresIsotropicTensor() override { return true; }

protected:
  virtual void initQpStatefulProperties() override;

  /**
   * Propagate the properties pertaining to this intermediate class.  This
   * is intended to be called from propagateQpStatefulProperties() in
   * classes that inherit from this one.
   * This is intentionally named uniquely because almost all models that derive
   * from this class have their own stateful properties, and this forces them
   * to define their own implementations of propagateQpStatefulProperties().
   */
  void propagateQpStatefulPropertiesRadialReturn();

  /**
   * Perform any necessary initialization before return mapping iterations
   * @param effective_trial_stress Effective trial stress
   * @param elasticityTensor     Elasticity tensor
   */
  virtual void computeStressInitialize(const ADDenseVector & /*effective_trial_stress*/,
                                       const ADRankFourTensor & /*elasticity_tensor*/)
  {
  }

  /**
   * Perform any necessary steps to finalize state after return mapping iterations
   * @param inelasticStrainIncrement Inelastic strain increment
   */
  virtual void computeStressFinalize(const ADRankTwoTensor & inelasticStrainIncrement,
                                     const ADReal & delta_gamma,
                                     ADRankTwoTensor & stress) = 0;
  /**
   * Perform any necessary steps to finalize strain increment after return mapping iterations
   * @param inelasticStrainIncrement Inelastic strain increment
   */
  virtual void computeStrainFinalize(ADRankTwoTensor & /*inelasticStrainIncrement*/,
                                     const ADRankTwoTensor & /*stress*/,
                                     const ADReal & /*delta_gamma*/)
  {
    mooseError("computeStrainFinalize needs to be implemented by a child class.");
  }

  void outputIterationSummary(std::stringstream * iter_output,
                              const unsigned int total_it) override;

  /// 2 * shear modulus
  ADReal _two_shear_modulus;

  ADMaterialProperty<Real> & _effective_inelastic_strain;
  const MaterialProperty<Real> & _effective_inelastic_strain_old;
  Real _max_inelastic_increment;
  const bool _apply_strain;
};
