Contributing
============

Contributions are welcome, and they are greatly appreciated!

Bug reports
-----------

When [reporting a bug](https://github.com/openSUSE/dbxincluder/issues),
always include:

-   Your operating system name and version.
-   Any details about your local setup that might be helpful in troubleshooting.
-   Detailed steps to reproduce the bug.

Documentation improvements
--------------------------

This could always use more documentation,
whether in the form of docstrings, additions to the man page or the creation of
a manual (currently non-existent).

Feature requests and feedback
-----------------------------

The best way to send feedback is to file an issue at
<https://github.com/openSUSE/dbxincluder/issues>.

If you are proposing a feature:

-   Explain in detail how it would work.
-   Keep the scope as narrow as possible, to make it easier to implement.

Development
-----------

To set up dbxincluder for local development:

1.  [Fork dbxincluder on GitHub](https://github.com/openSUSE/dbxincluder/fork).
2.  Clone your fork locally:

        git clone git@github.com:your_name_here/dbxincluder.git

3.  Create a branch for local development:

        git flow feature start name-of-your-bugfix-or-feature

    Now you can make your changes locally.

4.  When you're done making changes, run all the checks, doc builder and
    spell checker with [tox](http://tox.readthedocs.org/en/latest/install.html):

        tox

5.  Commit your changes and push your branch to GitHub:

        git add .
        git commit -m "Your detailed description of your changes."
        git flow feature publish

6.  Submit a pull request through the GitHub website.

### Pull Request Guidelines

If you need some code review or feedback while you're developing the code just make the pull request.

For merging, you should:

1.  Include passing tests (run `tox`) [1].
2.  Update documentation when there's new API, functionality etc.
3.  Add a note to `CHANGELOG.rst` about the changes.
4.  Add yourself to `AUTHORS.rst`.

### Tips

To run a subset of tests:

    tox -e envname -- py.test -k test_myfeature

To run all the test environments in *parallel* (you need to `pip install detox`):

    detox

[1] If you don't have all the necessary Python versions available locally, you
    can rely on Travis - it will
    [run the tests](https://travis-ci.org/openSUSE/dbxincluder/pull_requests)
    for each change you add to the pull request. However, that is a bit slower.
