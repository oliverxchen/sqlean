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

### Constraints

* Transformers are leaf to root, so cannot determine indent levels
* Visitors are leaf to root by default, but can be run root to leaf (visit_topdown)
