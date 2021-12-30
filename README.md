## Contributing

### Design principles

The identity of a tree should be sufficient to know how to inspect the children.
For example, suppose there were a `bool_operation` rule/tree that could be both
a binary or unary operation. This would break this principle since you wouldn't
know if the boolean operator is the 0th child (eg `NOT`) or the 1st child (eg
`AND` or `OR`).

All children of a tree should have the same indentation level.

As much as possible, parsing should follow BQ syntax. However, the BQ docs do
not provide a complete grammar.

You should be able to determine from a node itself what the indentation level
should be. In other words, you shouldn't need to look to the parent. This means
that anything that should be printed in full on it's own line needs to be a tree
and not a token.

#### CLI options vs configuration file

CLI options are for options that can change from one run of `sqlean` to another.
Project level configuration will not change from one run to another, and must be
set in `pyproject.toml`.
[`pyproject.toml`](https://snarky.ca/what-the-heck-is-pyproject-toml/) is
becoming the standard configuration for Python tooling, and no other
configuration files will be accepted by `sqlean`.

The `target` directory or file can be both a project level setting and also change
from one run to another, so it can appear in both `pyproject.toml` or as a CLI
argument. If it is in `pyproject.toml` and it is supplied as a CLI argument, then
CLI argument will be used. If it applies in neither, then the current directory
is used as a default.

### Constraints

* Transformers are leaf to root, so cannot determine indent levels
* Visitors are leaf to root by default, but can be run root to leaf (visit_topdown)
