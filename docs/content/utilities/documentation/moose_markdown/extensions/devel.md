# MOOSE Developer Extension (DevelExtension)

This extension includes the ability to list MooseDocs markdown configuration options and
commands settings. It also provides markdown sytnax for displaying the build status and
current MOOSE package download links.

!extension DevelExtension title=DevelExtension Configuration Options

## Build Status
!buildstatus https://moosebuild.org/mooseframework/ float=right padding-left=10px

You can add a Civet build status widget to any page using `!buildstatus http://url/to/civet`. Currently, this will only work with Civet continuous integration services.

```markdown
!buildstatus https://moosebuild.org/mooseframework/ float=right padding-left=10px
```
!!! note
    Be sure to follow your !buildstatus extension with an empty new line.

!extension-settings moose_build_status title=Command Settings (`!buildstatus`)


## Package Information
Creates syntax for reading MOOSE redistributable package names and links.

!extension-settings moose_package_parser title=Command Settings (`!moosepackage`)

## Extension Configuration and Settings

The devel extension also includes two commands (`!extension` and `!extension-settings`) for extracting and displaying the extension
configuration options as well as the settings for extension commands. For example, the following
commands are used within this markdown page.

* `!extension DevelExtension` <br>
This command displays the configuration options for the extension as a whole; these are the options
that may be specified in the configuration [YAML] file (e.g., website.yml).

* `!extension-settings moose_package_parser` <br>
This displays the optional key, value pairs that are passed to the individual commands contained
within the extension object. Automatic extraction of settings is only available for python objects
that inherit from MooseCommonExtension.

For both commands, if no configuration or settings are located the syntax is ignored and nothing
is displayed. This allows for the commands to be present in the markdown regardless if options are
available. But, if the underlying python code is changed to include options, they will display without modification
of the markdown.

!extension-settings moose_extension_config title=Command Settings (`!extension`)

!extension-settings moose_extension_component_settings title=Command Settings (`!extension-settings`)
