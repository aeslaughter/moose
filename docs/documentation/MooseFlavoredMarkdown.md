# Moose Flavored Markdown

## Including MOOSE Source Files

### Complete Code
You can include complete files from the repository using the `![]()` syntax similar to that used in images. For example, the following
includes the complete code as shown.

Notice that the a few settings are applied to customize the look of the catured code, a complete list of available settings is provided
in the [Settings](MooseFlavoredMarkdown.md#optional-settings) the included code.

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



### Optional Settings
The following options may be passed to control the how the output is formatted.

Option | Default | Description
------ | ------- | -----------
strip_header | True | Toggles the removal of the MOOSE copyright header.
github_link  | True | Include a link to the source code on GitHub.
overflow-y | Scroll | The action to take when the text overflow the html container (see [overflow-y](http://www.w3schools.com/cssref/css3_pr_overflow-y.asp)).
max-hieght | 500px | The maximum height of the code window (see [max-height](http://www.w3schools.com/cssref/pr_dim_max-height.asp)).
strip-extra-newlines | False | Remove exessive newlines from the included code.
