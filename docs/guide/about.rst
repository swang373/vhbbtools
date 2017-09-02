About
=====

The VHiggsBB analysis is one of the many physics analyses performed by the CMS
collaboration and, like the others, fields its own share of software frameworks
and scripts. The analysis pipeline starts with the Heppy ntuplizer, which
processes the data and Monte-Carlo simulation files into a common data format,
and ends with the data analysis frameworks used by the various analysts.

One such framework is Xbb_, which has endured a long and battle-tested history.
However, it is not the most friendly to new-comers or veterans:

.. _Xbb: https://github.com/perrozzi/Xbb

- The framework configuration can be clunky, with options scattered across
  multiple .ini files with non-intuively organized sections.
- The code takes its time on tasks that should have a quick turn-around. For
  example, after changing a cut, a new set of plots can take at least half an
  hour, and a new datacard can take as much as four hours!
- When searching for references and examples, sometimes the documentation is
  great, sometimes its outdated, and sometimes it doesn't exist at all.
- When perusing the source code for debugging, the presence of docstrings and
  inline comments are sporadic at best, and the inconsistent style makes
  parsing tiresome and time-consuming.
- Most times the options are set by the configuration files, but there are some
  cases where the user will have to modify the source code because of hard-coded
  behaviour, and that's if they know to do so!
- The framework now has a central repository and enjoys active development, but
  some analysis channels use forked versions which can no longer be merged back.

Even so, Xbb and its alternatives get the job done, so why does vhbbtools exist?
Well, vhbbtools is not "yet another framework", but a library which you can use
to enhance your framework of choice or write a quick one-off script. The goal of
vhbbtools is to enhance the quality of life of the current and next generation
of VHiggsBB analysts by:

- Abstracting away boilerplate code and common tasks behind classes and
  functions that are intuitive to use and well-documented.
- Adhering to Python idioms and best practices to preserve speed and keep
  resource use efficient.
- Maintaining an organized codebase that is publicly available and complete with
  documentation and usage examples to promote reproducible science.

By concerning itself with these details, vhbbtools better enables its users to
analyze the ever-growing mountain of LHC data collected by CMS.

