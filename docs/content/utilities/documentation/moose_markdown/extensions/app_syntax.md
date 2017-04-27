# AppSyntaxExtension

A set of special keywords exist for creating MOOSE specific links and tables within your markdown,
each are explained below. Note, the examples below refer to documentation associated with Kernels
and/or the Diffusion Kernel. This should be replaced by the syntax for the system or object being
documented.

!extension AppSyntaxExtension

## Class Description

* `!description /Kernels/Diffusion`: Inserts the class description (added via `addClassDescription` method) from the compiled application.
* `!parameters /Kernels/Diffusion`: Inserts tables describing the available input parameters for an object or action.
* `!inputfiles /Kernels/Diffusion`: Creates a list of input files that use the object or action.
* `!childobjects /Kernels/Diffusion`: Create a list of objects that inherit from the supplied object.
* `!subobjects /Kernels`: Creates a table of objects within the supplied system.
* `!subsystems /Adaptivity`: Creates a table of sub-systems within the supplied system.
