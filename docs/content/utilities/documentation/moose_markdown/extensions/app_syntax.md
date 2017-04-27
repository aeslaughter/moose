# AppSyntaxExtension

A set of special keywords exist for creating MOOSE specific links and tables within your markdown,
each are explained below. Note, the examples below refer to documentation associated with Kernels
and/or the Diffusion Kernel. This should be replaced by the syntax for the system or object being
documented.

!extension AppSyntaxExtension

## Class Description

The `!description` command adds an html paragraph with the content of InputParameters object
class descriptions, which is added in the MOOSE application within the `validParams` method.

For example, the [FileMesh] object includes a `validParams` function
as shown in \ref{file-mesh-valid-params}. Notice, that the `addClassDescription` method includes a short description of the object. To display this text the `!description` command is used followed
by the [MOOSE] input file syntax for the object as follows.

```
!description /Mesh/FileMesh style=color:green
```

!description /Mesh/FileMesh style=color:green

!listing framework/src/mesh/FileMesh.C start=template<> end=FileMesh::FileMesh id=file-mesh-valid-params caption=The validParams function from the [FileMesh] object.

!extension-settings moose_description caption=Command settings for `!description` command.

## Object Parameters

The `!parameters` command provides a means for displaying the default input file syntax for an
object. For example, considering the [FileMesh] object, the complete list of input syntax can be
provided using the following markdown command, the results of which are shown on the [FileMesh](framework/FileMesh.md#input-parameters) page.

```
!parameters /Mesh/FileMesh title=None
```

!extension-settings moose_parameters caption=Command settings for `!parameters` command.

## Input Files and Child Objects

In many cases it is useful to know where in the examples, tutorials, or tests an object is utilized
in an input file as well as what other objects may inherit from an object. Therefore, two commands
are provided to create these lists: `!inputfiles` and `!childobjects`, respectively.

!extension-settings moose_object_syntax caption=Command settings for `!inputfiles` and `!childobjects` commands.


* `!subobjects /Kernels`: Creates a table of objects within the supplied system.
* `!subsystems /Adaptivity`: Creates a table of sub-systems within the supplied system.


[FileMesh]: #input-parameters
