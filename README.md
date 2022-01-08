## Why

* rise of SQL
* dbt
* formatter like black to reduce arguments. In return for consistency, sometimes
  it's less readable


## Contributing

`sqlean` will need a community effort to be capable of parsing all valid SQL
queries. We've setup the testing to make it easier to add to the grammar so that
more and more elements of valid SQL can be parsed.

### Snapshot tests


#### Snapshot files

Each snapshot file is divided into 3 parts, with each part separated by:

```text

---

```

The first part is minimal working example (MWE) for the SQL query. This is the
only part that needs to be human-written.

#### Conventions

The snapshots are located in the `sqlean/tests/snapshots` directory, under
different sub-directories. The sub-directories are grouped by grammar elements.
Within each sub-directory, the files are prefixed by a three digit integer...

The snapshot files have extension `.snapshot`. You can set up your editor to
recognise the `.snapshot` file as an `R` file so that you get syntax
highlighting of the parse tree.

### Adding to the parser

If you run `sqlean` on a file that you contains a valid SQL/dbt query but
`sqlean` marks it as "unparsable", this indicates that there is an element of
your file that is not in `sqlean`'s grammar. You can contribute to the grammar
so that the element and the file can be parsed and styled.

1. TODO: there should be an easy command line way to figure out what element
   cannot be parsed.
1. Once the unparsable element has been identified, write a minimal working
   example (MWE) of an SQL query that contains the element.
1. Identify the sub-directory in the `sqlean/tests/snapshots` directory where
   the element should go, or if there needs to be a new sub-directory.
1. Within the sub-directories, create a new file named according to the
   [conventions](#conventions) and put your MWE in the file.
1. Run the snapshot test for this file:

   ```bash
   make snapshot L=tests/snapshots/{sub_dir}/{new_file}
   ```

   This will fail with an error printed in the snapshot file which can guide
   you on modifying the grammar so that the file can be parsed.

   If there are a number of different new files, you can use the `M` (match)
   argument instead of the `L` (location) argument to match a string within the
   file names. For example,

   ```bash
   make snapshot M=dbt
   ```

    will run the snapshot tests on all snapshot files that contain "dbt" in the
    file name.
1. As you modify the grammar in the `.lark` file, you can check the output of
   the parser by running the snapshot test and checking what is printed in the
   third section of the snapshot file. Errors will appear in the third section
   if there is a problem with the grammar.
1. Once you're happy with the parse tree, you can move on to styling the output.
   Similar to the grammar, as you modify the styling, you can check the output
   of the styler by running the same snapshot test and checking what is printed
   in the second section of the snapshot file. Errors will appear in the second
   section if there is a problem with the styler.
1. Once you're happy with the styling, you should run the tests on all existing
   snapshot files with:

   ```bash
   make snapshot
   ```

   If your parsing or styling changed other files, it will show up here. These
   file changes will show up in git so it will be easy to see for the author
   and in code review whether the change was intentional or not.




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
