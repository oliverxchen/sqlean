#!/usr/bin/env python

# we use poetry for our build, but this file seems to be required
# in order to get GitHub dependencies graph to work.
# via https://patrick.wtf/posts/til-how-to-show-dependents-packages-on-github-when-using-poetry
# and https://github.com/Textualize/rich/blob/bf23d03893305d974e1ad9f44cfc45d71903a243/setup.py
import setuptools


if __name__ == "__main__":
    setuptools.setup(name="sqlean")
