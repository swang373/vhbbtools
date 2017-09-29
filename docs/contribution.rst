Contribution
============

If you would like to contribute to vhbbtools, feel free to clone the repository
or fork the project. To keep the git workflow simple, please create feature
branches based on the master branch. When your new feature is ready, or you
would like to initiate a discussion about your feature, submit a pull request.

As the project matures, expect more information about conventions and practices
to appear. For now, the following guidelines suffice:

* Python code should adhere to the PEP 8 style guide.
* Document your code using NumPy style docstrings!
* Feature branches should have a clear and concise name describing the feature
  under development.

Editing and Building the Documentation
--------------------------------------

Editing the documentation and adding new documentation pages follows the same
process as developing new features. The documentation is written in
`reStructuredText`_ and generated using `Sphinx`_, so some familiarity with
them is encouraged. You can also peruse the source of the current documentation
for usage examples.

.. _Sphinx: http://www.sphinx-doc.org/en/stable/index.html
.. _reStructuredText: http://www.sphinx-doc.org/en/stable/rest.html

1. Clone the repository, create a new documentation feature branch, and change
   to the ``docs`` directory which contains the documentation source files.

   .. code-block:: bash

      git clone git@github.com:swang373/vhbbtools.git
      cd vhbbtools
      git checkout -b my_new_docs
      cd docs

2. Edit any of the existing documentation files, adding new ones as needed.

3. Install Sphinx if it isn't already installed, then build the documentation
   to check that your changes compile without errors:

   .. code-block:: bash

      pip install sphinx
      make html

   The build products will be placed within a new directory called ``_build``.

4. Preview your changes by opening the file ``_build/html/index.html`` in your
   web browser of choice. This is a good time to check that your edits render
   as you expect and nothing else breaks.

5. Repeat steps 2-4 until you are satisfied with your changes, then commit
   them and push your branch upstream.

6. Submit a pull request to incorporate your improvements into the official
   documentation!

Building the Documentation for GitHub Pages
-------------------------------------------

This section is mainly relevant to the documentation maintainers. The sources
for the documentation website are tracked by the ``gh-pages`` branch for hosting
via `GitHub Pages`_. As the documentation receives updates, new builds of the
documentation website will need to be committed to the ``gh-pages`` branch to
keep the live documentation up to date.

.. _GitHub Pages: https://pages.github.com/

1. Clone the main repository.

   .. code-block:: bash

      git clone git@github.com:swang373/vhbbtools.git

2. Create a new directory next to the aforementioned clone to serve as the build
   directory. Inside the new directory, clone the main repository again and then
   checkout the ``gh-pages`` branch:

   .. code-block:: bash

      mkdir vhbbtools-gh-pages
      cd vhbbtools-gh-pages
      git clone git@github.com:swang373/vhbbtools.git html
      git checkout gh-pages

   The main repository is cloned into the directory ``html`` in anticipation
   that it will contain the build products of the updated documentation.

3. Change to the ``docs`` directory of the first clone and, assuming Sphinx is
   already installed, build the documentation using the following commands:

   .. code-block:: bash

      cd ../vhbbtools/docs
      make html BUILDDIR=../../vhbbtools-gh-pages

   The BUILDDIR option must be set to the path of the build directory created
   in step 2.

4. Once the build succeeds, change to the ``html`` directory inside the build
   directory, commit all of the files, and then push the new commit upstream:

   .. code-block:: bash

      cd ../../vhbbtools-gh-pages/html
      git add .
      git commit -m "New build for the live documentation"
      git push origin gh-pages

   The live documentation at https://www.swang373.github.io/vhbbtools will be
   updated to reflect the latest build. It may take a minute or two for the
   changes to appear.

