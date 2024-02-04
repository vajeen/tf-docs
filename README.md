# TF-Doc

``tfdocs` lets you generate `README.md` for Terraform modules based on `variables.tf`.
Additionally, it can sort variable definitions.

# Usage

    tfdocs [flags]

`tfdocs` will create or update README.md in the current directory. Alternatively, you can mark s section of the README.md file with below tags `tfdocs` will only replace the content between these markers.

## Example

    # My module
    This is a module to do something.

    <!-- TFDOCS START -->

    This section will be replaced by tfdocs.

    <!-- TFDOCS END -->

    # End of README


**Note**: ``tfdocs` overwrite an existing README.md file. It's always good to use `--dry-run` first.
    
Flags:

        -h, --help      help for tfdocs
        

# Authors

tfdocs is created and maintained by [vajeen].
