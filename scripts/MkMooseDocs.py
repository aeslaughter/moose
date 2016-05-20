#!/usr/bin/env python
import os
import MooseDocs


if __name__ == '__main__':


    # Args Parse


    # Locate an executable
    app = os.path.join(MooseDocs.MOOSE_DIR, 'test', 'moose_test-opt')
    args = '--yaml'
    raw = runExe(app, args)

    print raw

    """
    ydata = YamlData(raw)

    path = '/Kernels/Diffusion'
    info = MooseObjectInformation(ydata[path])

    print info
    """
