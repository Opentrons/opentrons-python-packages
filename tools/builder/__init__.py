"""
builder: the package that builds the packages

Because the package build system is complex and is in a python ecosystem, we
use python for our build orchestration. The build orchestration system all
lives here.

KEEP THIS FILE AND ITS IMPORTS FREE OF EXTERNAL DEPENDENCIES. This package is
used both inside the container, where it's okay to use whatever you want as long
as it's in poetry; and outside the container, where we really want to let people
run the builder using only a base python install and docker. Code in builder.common
or builder.host must be runnable in this way, and importing builder.host or
builder.common will run whatever code is in this file. Any other subpackage is
fair game.
"""

__version__ = "0.0.1+992e55e.dirty"
