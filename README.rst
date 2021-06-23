# Contributing

## Design principles

The identity of a tree should be sufficient to know how to inspect the children.
For example, suppose there were a `bool_operation` rule/tree that could be both
a binary or unary operation. This would break this principle since you wouldn't
know if the boolean operator is the 0th child (eg `NOT`) or the 1st child (eg
`AND` or `OR`).
