# joanharvard

[@mchris4duke wondered](https://twitter.com/mchris4duke/status/604723555293622272) if anyone had
counted male vs female authors in library collections, so I'm taking a stab at that with the
[Harvard open metadata dump](http://openmetadata.lib.harvard.edu/bibdata). (I've kept the data
dump out of this repo because it's super gigantic, but you can readily download your own, if
you have a spare hour.)

There are roughly a million caveats with this approach, which are detailed in the `guesser.py`
docstring.

Things it'd be great to do with this with codebase (or its methodology) include:
* edits for modularity, improved error-handling, and style
* expanding to handle MARC's 700 field; this requires answering methodological questions about
  the right way to count books with authors of multiple genders
* anything that addresses caveats in the docstring
* quality time spent with the metadata to see if there are more edge cases we can adequately address
