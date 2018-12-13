import logging
import vtk
import chigger
from ChiggerFilter import ChiggerFilter

class ExtractBlockFilter(ChiggerFilter):
    VTKFILTERTYPE = vtk.vtkExtractBlock

    def __init__(self, *args, **kwargs):
        ChiggerFilter.__init__(self, *args, **kwargs)

        self.SetNumberOfInputPorts(1)
        self.InputType = 'vtkMultiBlockDataSet'

        self.SetNumberOfOutputPorts(1)
        self.OutputType = 'vtkMultiBlockDataSet'


    def RequestData(self, request, inInfo, outInfo):
        self.log('RequestData', level=logging.DEBUG)

        inp = inInfo[0].GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        opt = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())

        result = self.getChiggerResult()
        reader = result.getInput()

        block_info = reader.getBlockInformation()
        def get_indices(option, vtk_type):
            """Helper to populate vtkExtractBlock object from selected blocks/sidesets/nodesets"""
            indices = []
            blocks = result.getOption(option)
            if blocks:
                for vtkid, item in block_info[vtk_type].iteritems():
                    for name in blocks:
                        if (item.name == str(name)) or (str(name) == vtkid):
                            indices.append(item.multiblock_index)
            return indices

        extract_indices = get_indices('block', chigger.exodus.ExodusReader.BLOCK)
        extract_indices += get_indices('boundary', chigger.exodus.ExodusReader.SIDESET)
        extract_indices += get_indices('nodeset', chigger.exodus.ExodusReader.NODESET)

        self._vtkfilter.RemoveAllIndices()
        for index in extract_indices:
            self._vtkfilter.AddIndex(index)

        self._vtkfilter.SetInputData(inp)
        self._vtkfilter.Update()
        opt.ShallowCopy(self._vtkfilter.GetOutput())

        return 1
