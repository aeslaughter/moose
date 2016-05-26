# Moose Flavored Markdown


## Including MOOSE C++ Code
### Complete MOOSE Source Code
You can include complete files from the repository using the `![]()` syntax similar to that used in images. For example, the following
includes the complete code as shown.

```text
![Diffusion.C](framework/src/kernels/Diffusion.C)
```

![Diffusion.C](framework/src/kernels/Diffusion.C github_link:True)

#### Settings
The following options may be passed to control the how the output is formatted.

Option | Default | Description
------ | ------- | -----------
strip_header | True | Toggles the removal of the MOOSE copyright header.
github_link  | True | Include a link to the source code on GitHub.

![adfa](nope/file.i)
