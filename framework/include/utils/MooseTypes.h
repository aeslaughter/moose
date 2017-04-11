/****************************************************************/
/*               DO NOT MODIFY THIS HEADER                      */
/* MOOSE - Multiphysics Object Oriented Simulation Environment  */
/*                                                              */
/*           (c) 2010 Battelle Energy Alliance, LLC             */
/*                   ALL RIGHTS RESERVED                        */
/*                                                              */
/*          Prepared by Battelle Energy Alliance, LLC           */
/*            Under Contract No. DE-AC07-05ID14517              */
/*            With the U. S. Department of Energy               */
/*                                                              */
/*            See COPYRIGHT for full restrictions               */
/****************************************************************/

#ifndef MOOSETYPES_H
#define MOOSETYPES_H

#include "Moose.h"

// libMesh includes
#include "libmesh/libmesh.h"
#include "libmesh/id_types.h"
#include "libmesh/stored_range.h"
#include "libmesh/elem.h"
#include "libmesh/petsc_macro.h"
#include "libmesh/boundary_info.h"

#include <string>
#include <vector>
#include <memory>

// Forward Declarations
class MultiMooseEnum;

// DO NOT USE (Deprecated)
#define MooseSharedPointer std::shared_ptr
#define MooseSharedNamespace std

/**
 * Macro for inferring the proper type of a normal loop index compatible
 * with the "auto" keyword.
 * Usage:
 *   for (auto i = beginIndex(v); i < v.size(); ++i)    // default index is zero
 *   for (auto i = beginIndex(v, 1); i < v.size(); ++i) // index is supplied
 */
// The multiple macros that you would need anyway [as per: Crazy Eddie (stack overflow)]
#ifdef __clang__
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wgnu-zero-variadic-macro-arguments"
#endif

#define beginIndex_0() ERROR-- > "beginIndex() requires one or two arguments"
#define beginIndex_1(A) decltype(A.size())(0)
#define beginIndex_2(A, B) decltype(A.size())(B)
#define beginIndex_3(A, B, C) ERROR-- > "beginIndex() requires one or two arguments"
#define beginIndex_4(A, B, C, D) ERROR-- > "beginIndex() requires one or two arguments"

// The interim macro that simply strips the excess and ends up with the required macro
#define beginIndex_X(x, A, B, C, D, FUNC, ...) FUNC

// The macro that the programmer uses
#define beginIndex(...)                                                                            \
  beginIndex_X(,                                                                                   \
               ##__VA_ARGS__,                                                                      \
               beginIndex_4(__VA_ARGS__),                                                          \
               beginIndex_3(__VA_ARGS__),                                                          \
               beginIndex_2(__VA_ARGS__),                                                          \
               beginIndex_1(__VA_ARGS__),                                                          \
               beginIndex_0(__VA_ARGS__))
#ifdef __clang__
#pragma clang diagnostic pop
#endif

/**
 * MOOSE typedefs
 */
typedef Real PostprocessorValue;
typedef std::vector<Real> VectorPostprocessorValue;
typedef boundary_id_type BoundaryID;
typedef unsigned int InterfaceID;
typedef subdomain_id_type SubdomainID;
typedef unsigned int MooseObjectID;
typedef unsigned int THREAD_ID;

typedef StoredRange<std::vector<dof_id_type>::iterator, dof_id_type> NodeIdRange;
typedef StoredRange<std::vector<const Elem *>::iterator, const Elem *> ConstElemPointerRange;

// The execute_on system in MOOSE relies on integer flags for storage and execution commands. The
// validParams functions of the object (via SetupInterface) utilizes MultiMooseEnum for input
// file syntax. In order to create arbitrary flags that are consistent and cause compiler errors
// rather than runtime errors the registerExecFlag was defined to create two global values that are
// needed for working with the new flags. For example, calling registerExecFlag(FOO, 12345) creates:
//    EXEC_FOO = 12345
//    EXEC_FOO_NAME = "FOO"
//
// Notice that the variables created by this macro are re-defined each time this header it included,
// this was by design to avoid requiring a separate definition and declaration macros.
typedef int ExecFlagType;
typedef std::string ExecFlagName;
#define registerExecFlag(name, number)                                                             \
  const ExecFlagType EXEC_##name(number);                                                          \
  const ExecFlagName EXEC_##name##_NAME(#name);

// Previously ExecFlagType was an C++ enum. However, this did not allow for custom execute flags
// to be defined and required a lot of conversion back and forth between the MultiMooseEnum and
// the actual enum. The enum has now been replaced, but to allow other codes to continue to
// operate without being modified this list of globals is defined.
registerExecFlag(NONE, 0x00);           // 0
registerExecFlag(INITIAL, 0x01);        // 1
registerExecFlag(LINEAR, 0x02);         // 2
registerExecFlag(NONLINEAR, 0x04);      // 4
registerExecFlag(TIMESTEP_END, 0x08);   // 8
registerExecFlag(TIMESTEP_BEGIN, 0x10); // 16
registerExecFlag(FINAL, 0x20);          // 32
registerExecFlag(FORCED, 0x40);         // 64
registerExecFlag(FAILED, 0x80);         // 128
registerExecFlag(CUSTOM, 0x100);        // 256
registerExecFlag(SUBDOMAIN, 0x200);     // 512

extern std::map<int, std::string> exec_flag_to_name;

namespace Moose
{
const SubdomainID ANY_BLOCK_ID = libMesh::Elem::invalid_subdomain_id - 1;
const SubdomainID INVALID_BLOCK_ID = libMesh::Elem::invalid_subdomain_id;
const BoundaryID ANY_BOUNDARY_ID = static_cast<BoundaryID>(-1);
const BoundaryID INVALID_BOUNDARY_ID = libMesh::BoundaryInfo::invalid_id;


/**
 * MaterialData types
 *
 * @see FEProblemBase, MaterialPropertyInterface
 */
enum MaterialDataType
{
  BLOCK_MATERIAL_DATA,
  BOUNDARY_MATERIAL_DATA,
  FACE_MATERIAL_DATA,
  NEIGHBOR_MATERIAL_DATA
};

/**
 * Flag for AuxKernel related execution type.
 */
enum AuxGroup
{
  PRE_AUX = 0,
  POST_AUX = 1,
  ALL = 2
};

/**
 * Framework-wide stuff
 */
enum VarKindType
{
  VAR_NONLINEAR,
  VAR_AUXILIARY
};

enum KernelType
{
  KT_TIME = 0,
  KT_NONTIME = 1,
  KT_NONEIGEN = 2,
  KT_EIGEN = 3,
  KT_ALL
};

enum CouplingType
{
  COUPLING_DIAG,
  COUPLING_FULL,
  COUPLING_CUSTOM
};

enum ConstraintSideType
{
  SIDE_MASTER,
  SIDE_SLAVE
};

enum DGResidualType
{
  Element,
  Neighbor
};

enum DGJacobianType
{
  ElementElement,
  ElementNeighbor,
  NeighborElement,
  NeighborNeighbor
};

enum ConstraintType
{
  Slave = Element,
  Master = Neighbor
};

enum ConstraintJacobianType
{
  SlaveSlave = ElementElement,
  SlaveMaster = ElementNeighbor,
  MasterSlave = NeighborElement,
  MasterMaster = NeighborNeighbor
};

enum CoordinateSystemType
{
  COORD_XYZ,
  COORD_RZ,
  COORD_RSPHERICAL
};

/**
 * Preconditioning side
 */
enum PCSideType
{
  PCS_LEFT,
  PCS_RIGHT,
  PCS_SYMMETRIC
};

/**
 * Type of the solve
 */
enum SolveType
{
  ST_PJFNK,  ///< Preconditioned Jacobian-Free Newton Krylov
  ST_JFNK,   ///< Jacobian-Free Newton Krylov
  ST_NEWTON, ///< Full Newton Solve
  ST_FD,     ///< Use finite differences to compute Jacobian
  ST_LINEAR  ///< Solving a linear problem
};

/**
 * Type of the eigen solve
 */
enum EigenSolveType
{
  EST_POWER,          ///< Power / Inverse / RQI
  EST_ARNOLDI,        ///< Arnoldi
  EST_KRYLOVSCHUR,    ///< Krylov-Schur
  EST_JACOBI_DAVIDSON ///< Jacobi-Davidson
};

/**
 * Type of the eigen problem
 */
enum EigenProblemType
{
  EPT_HERMITIAN,            ///< Hermitian
  EPT_NON_HERMITIAN,        ///< Non-Hermitian
  EPT_GEN_HERMITIAN,        ///< Generalized Hermitian
  EPT_GEN_INDEFINITE,       ///< Generalized Hermitian indefinite
  EPT_GEN_NON_HERMITIAN,    ///< Generalized Non-Hermitian
  EPT_POS_GEN_NON_HERMITIAN ///< Generalized Non-Hermitian with positive (semi-)definite B
};

/**
 * Which eigen pairs
 */
enum WhichEigenPairs
{
  WEP_LARGEST_MAGNITUDE,  ///< largest magnitude
  WEP_SMALLEST_MAGNITUDE, ///< smallest magnitude
  WEP_LARGEST_REAL,       ///< largest real
  WEP_SMALLEST_REAL,      ///< smallest real
  WEP_LARGEST_IMAGINARY,  ///< largest imaginary
  WEP_SMALLEST_IMAGINARY, ///< smallest imaginary
  WEP_TARGET_MAGNITUDE,   ///< target magnitude
  WEP_TARGET_REAL,        ///< target real
  WEP_TARGET_IMAGINARY,   ///< target imaginary
  WEP_ALL_EIGENVALUES     ///< all eigenvalues
};

/**
 * Type of constraint formulation
 */
enum ConstraintFormulationType
{
  Penalty,
  Kinematic
};
/**
 * Type of the line search
 */
enum LineSearchType
{
  LS_INVALID, ///< means not set
  LS_DEFAULT,
  LS_NONE,
  LS_BASIC,
#ifdef LIBMESH_HAVE_PETSC
#if PETSC_VERSION_LESS_THAN(3, 3, 0)
  LS_CUBIC,
  LS_QUADRATIC,
  LS_BASICNONORMS,
#else
  LS_SHELL,
  LS_L2,
  LS_BT,
  LS_CP
#endif
#endif
};
}

/**
 * This Macro is used to generate std::string derived types useful for
 * strong type checking and special handling in the GUI.  It does not
 * extend std::string in any way so it is generally "safe"
 */
#define DerivativeStringClass(TheName)                                                             \
  class TheName : public std::string                                                               \
  {                                                                                                \
  public:                                                                                          \
    TheName() : std::string() {}                                                                   \
    TheName(const std::string & str) : std::string(str) {}                                         \
    TheName(const std::string & str, size_t pos, size_t n = npos) : std::string(str, pos, n) {}    \
    TheName(const char * s, size_t n) : std::string(s, n) {}                                       \
    TheName(const char * s) : std::string(s) {}                                                    \
    TheName(size_t n, char c) : std::string(n, c) {}                                               \
  } /* No semicolon here because this is a macro */

// Instantiate new Types

/// This type is for expected filenames, it can be used to trigger open file dialogs in the GUI
DerivativeStringClass(FileName);

/// This type is for expected filenames where the extension is unwanted, it can be used to trigger open file dialogs in the GUI
DerivativeStringClass(FileNameNoExtension);

/// This type is similar to "FileName", but is used to further filter file dialogs on known file mesh types
DerivativeStringClass(MeshFileName);

/// This type is for output file base
DerivativeStringClass(OutFileBase);

/// This type is used for objects that expect nonlinear variable names (i.e. Kernels, BCs)
DerivativeStringClass(NonlinearVariableName);

/// This type is used for objects that expect Auxiliary variable names (i.e. AuxKernels, AuxBCs)
DerivativeStringClass(AuxVariableName);

/// This type is used for objects that expect either Nonlinear or Auxiliary Variables such as postprocessors
DerivativeStringClass(VariableName);

/// This type is used for objects that expect Boundary Names/Ids read from or generated on the current mesh
DerivativeStringClass(BoundaryName);

/// This type is similar to BoundaryName but is used for "blocks" or subdomains in the current mesh
DerivativeStringClass(SubdomainName);

/// This type is used for objects that expect Postprocessor objects
DerivativeStringClass(PostprocessorName);

/// This type is used for objects that expect VectorPostprocessor objects
DerivativeStringClass(VectorPostprocessorName);

/// This type is used for objects that expect Moose Function objects
DerivativeStringClass(FunctionName);

/// This type is used for objects that expect Moose Distribution objects
DerivativeStringClass(DistributionName);

/// This type is used for objects that expect "UserObject" names
DerivativeStringClass(UserObjectName);

/// This type is used for objects that expect an Indicator object name
DerivativeStringClass(IndicatorName);

/// This type is used for objects that expect an Marker object name
DerivativeStringClass(MarkerName);

/// This type is used for objects that expect an MultiApp object name
DerivativeStringClass(MultiAppName);

/// Used for objects the require Output object names
DerivativeStringClass(OutputName);

/// Used for objects that expect MaterialProperty names
DerivativeStringClass(MaterialPropertyName);

/// User for accessing Material objects
DerivativeStringClass(MaterialName);

#endif // MOOSETYPES_H
