#* This file is part of MOOSETOOLS repository
#* https://www.github.com/idaholab/moosetools
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moosetools/blob/main/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

import os
import packaging.version
from moosetools import mooseutils
from moosetools.parameters import InputParameters
from moosetools.moosetest.controllers import AutotoolsConfigController, AutotoolsConfigItem

class LibMeshConfigController(AutotoolsConfigController):
    """
    A base `Controller` to dictate if an object should run based on a C++ configuration.
    """
    @staticmethod
    def validParams():
        params = AutotoolsConfigController.validParams()
        params.setValue('prefix', 'libmesh')
        return params

    @staticmethod
    def validObjectParams():
        """
        Return an `parameters.InputParameters` object to be added to a sub-parameter of an object
        with the name given in the "prefix" parameter
        """
        params = AutotoolsConfigController.validObjectParams()

        # libMesh features
        params.add('mesh_mode', vtype=str, allow=('REPLICATED', 'DISTRIBUTED'),
                   doc="Require a specific parallel mesh mode.",
                   user_data=AutotoolsConfigItem('LIBMESH_ENABLE_PARMESH', '0', {'0':'REPLICATED', '1':'DISTRIBUTED'}))
        params.add('dof_id_bytes', vtype=int,
                   doc="Require certain number of bytes for the `dof_id` type.",
                   user_data=AutotoolsConfigItem('LIBMESH_DOF_ID_BYTES', '4', int))

        params.add('unique_id', vtype=bool,
                   doc="The configured parallel mesh mode.",
                   user_data=AutotoolsConfigItem('LIBMESH_ENABLE_UNIQUE_ID', '0', bool))

        # Additional, external libraries
        params.add('dtk', vtype=bool,
                   doc="Require the existence of DTK library.",
                   user_data=AutotoolsConfigItem('LIBMESH_TRILINOS_HAVE_DTK', '0', bool))
        params.add('boost', vtype=bool,
                   doc="Require the existence of external BOOST library.",
                   user_data=AutotoolsConfigItem('LIBMESH_HAVE_EXTERNAL_BOOST', '0', bool))
        params.add('vtk', vtype=bool,
                   doc="Require the existence of VTK library.",
                   user_data=AutotoolsConfigItem('LIBMESH_HAVE_VTK', '0', bool))
        params.add('tecplot', vtype=bool,
                   doc="Require the existence of Tecplot library.",
                   user_data=AutotoolsConfigItem('LIBMESH_HAVE_TECPLOT_API', '0', bool))
        params.add('curl', vtype=bool,
                   doc="Require the existence of Curl library.",
                   user_data=AutotoolsConfigItem('LIBMESH_HAVE_CURL', '0', bool))
        params.add('slepc', vtype=bool,
                   doc="Require the existence of SLEPc library.",
                   user_data=AutotoolsConfigItem('LIBMESH_HAVE_SELPC', '0', bool))
        params.add('fparser_jit', vtype=bool,
                   doc="Require the existence of just-in-time (JIT) fparser library.",
                   user_data=AutotoolsConfigItem('LIBMESH_HAVE_FPARSER_JIT', '0', bool))

        # Threading
        params.add('threads', vtype=bool,
                   doc="Require use of threading.",
                   user_data=AutotoolsConfigItem('LIBMESH_USING_THREADS', '0', bool))
        params.add('tbb', vtype=bool,
                   doc="Require use of Intel Threading Building Blocks (TBB) library.",
                   user_data=AutotoolsConfigItem('LIBMESH_HAVE_TBB_API', '0', bool))
        params.add('openmp', vtype=bool,
                   doc="Require use of OpenMP threading.",
                   user_data=AutotoolsConfigItem('LIBMESH_USING_OPENMP', '0', bool))

        return params
