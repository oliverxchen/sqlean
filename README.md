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

### Thoughts

How do we know what should have `indent_level = 0`?

If `has_parent = 0`? Not really, because we can have a config block, a with
clause and query that should all be `indent_level = 0`.

How about if we start with `query_file` and and all direct children of that have
`indent_level = 0`?

custom trees
<https://github.com/lark-parser/lark/issues/676>

### Constraints

* Visitors can add attributes, but Transformers can't see them
* Transformers are leaf to root, so cannot determine indent levels
* Visitors are leaf to root by default, but can be run root to leaf (visit_topdown)

## Things to change about the parsing

* `table_name`should distinguish between single name and project/dataset/table
* maybe inline the from_item
* join_operation should be inlined
* suppress LPAR and RPAR
* functions in select_item (wrapped in base_expression) and arg_item (bare) are
  parsed differently
