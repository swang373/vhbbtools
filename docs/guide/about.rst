About
=====

The VHiggsBB analysis is one of the many physics analyses performed by the CMS
collaboration and, like the others, fields its own share of software frameworks
and scripts. The analysis pipeline starts with the Heppy ntuplizer, which
processes the data and Monte-Carlo simulation files into a common data format,
and ends with the data analysis frameworks used by the analysts.

The current data analysis frameworks are battle-tested, batteries included
behemoths which have endured for generations of datasets and analysts. As
powerful as they are in automating the workflows they were designed for:

- Some of them aren't so nimble anymore and struggle to scale in terms of speed
  and resource use as datasets continue to grow.
- Their documentation is great in some places, outdated in others, and often
  just doesn't exist. Analysts end up learning to use these frameworks through
  a mix of oral tradition and trial and error.
- Debugging their source code can be time-consuming given the sporadic presence
  of docstrings and inconsistent style, while extending their source code can
  be dangerous because of hard-coded assumptions in unexpected places.

The vhbbtools package was written to address those drawbacks by:

- Staying simple. By focusing on dataset access and data manipulation,
  the package can be incorporated into your framework of choice without
  disrupting its workflow.
- Adhering to Python best practices to preserve speed and maintain efficient
  resource usage.
- Maintaining an organized codebase with a permissive license to promote
  open and collaborative science.
- Maintaining documentation complete with usage examples for the benefit of
  current and next generation VHiggsBB analysts.

