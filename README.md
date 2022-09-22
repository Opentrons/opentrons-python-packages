# opentrons-python-packages
A repository hosting prebuilds of Python packages suitable for installing on an Opentrons robot.

**This repository is under construction and the code here has not yet been released.**

The OT-2 uses a custom Buildroot-created Linux system running on a Raspberry Pi. Because it is a custom system, it cannot use binary python packages made with Raspbian in mind; because it is an arm7hf architecture, it cannot use more general manylinux wheels made with x86-64 or arm64 in mind. Since the OT-2 itself does not have a compiler, we use this repository to provide prebuilt python wheels that are installable on an OT-2 by using a [PEP-503](https://peps.python.org/pep-0503) simple package index.

Any package identified here can be installed on an OT-2 through `pip`.

## Requesting Packages

Please open an issue if there is a Python package that you want that is not present, or if there is a specific version of a Python package that the index does not have. Please also feel free to open a pull request to add it! Before requesting a package or new version, please try installing it on an OT-2 first; only packages with native code components need to be here, since pure-python packages are installable from PyPI.

Be aware that the OT-2 system can't always handle the addition of a specific package. For instance, the package might be a thin wrapper around a system library that is not available on the OT-2; or it might have a toolchain that does not allow cross-compilation with the tools we have available.
