# Moose Flavored Markdown


## Including MOOSE Source Files
It is possible to include complete or partial C++ or input files from the local MOOSE repository. The following sections detail the custom
markdown syntax to needed, including the application of special settings in the form of key, value pairings that are supplied within
the custom markdown. A complete list of available settings is provided in the [Settings](MooseFlavoredMarkdown.md#optional-settings) the included code.

### Complete C++ Code
You can include complete files from the repository using the `![]()` syntax similar to that used in images. For example, the following
includes the complete code as shown.

```text
![Diffusion.C](framework/src/kernels/Diffusion.C max-height=200px strip-extra-newlines=True)
```

![Diffusion.C](framework/src/kernels/Diffusion.C max-height=200px strip-extra-newlines=True)


### Class Methods
By including a method name, in C++ syntax fashion, it is possible to include specific methods from C++ class in MOOSE. For example,
the following limits the included code to the `computeQpResidual` method.

```text
![Diffusion.C::computeQpResidual](framework/src/kernels/Diffusion.C::computeQpResidual)
```

![Diffusion.C::computeQpResidual](framework/src/kernels/Diffusion.C::computeQpResidual)


### Complete Input File
In similar fashion as in shown in [Complete C++ Code](MooseFlavoredMarkdown.md#complete-c++-code), input files may also be include
as follows.

```text
![simple_diffusion.i](test/tests/kernels/simple_diffusion/simple_diffusion.i strip-extra-newlines=True max-height=300px)
```

![simple_diffusion.i](test/tests/kernels/simple_diffusion/simple_diffusion.i strip-extra-newlines=True max-height=300px)


### Input File Block
By including a block name the included content will be limited to the content matching the supplied name. Notice that the supplied name may be approximate; however, if it is not unique only the first match will appear.

```
![simple_diffusion.i](test/tests/kernels/simple_diffusion/simple_diffusion.i::Kernels)
```


![simple_diffusion.i](test/tests/kernels/simple_diffusion/simple_diffusion.i::Kernels repo_link=True)


### Optional Settings
The following options may be passed to control the how the output is formatted.

Option               | Default | Description
-------------------- | ------- | -----------
strip_header         | True    | Toggles the removal of the MOOSE copyright header.
repo_link          | True    | Include a link to the source code on GitHub ("label" must be True).
label                | True    | Include a label with the filename before the code content block.
overflow-y           | Scroll  | The action to take when the text overflow the html container (see [overflow-y](http://www.w3schools.com/cssref/css3_pr_overflow-y.asp)).
max-hieght           | 500px   | The maximum height of the code window (see [max-height](http://www.w3schools.com/cssref/pr_dim_max-height.asp)).
strip-extra-newlines | False   | Remove exessive newlines from the included code.

## Slideshows
