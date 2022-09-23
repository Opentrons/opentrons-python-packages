"""
builder.common: code shared between host and container sides.

Code here MUST NOT import any python library not in the standard library. We
want this common code to exist so it can centralize things like arguments, but
it needs to be callable outside the poetry environment, so it can't use dependencies.
"""
