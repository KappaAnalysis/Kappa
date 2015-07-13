Skim configuration files for Z+Jet skims
========================================

These are CMSSW configurations and grid-control configurations for Kappa skims
of the Z+jet and jet-calibration group: Joram Berger and Dominik Haitz.

In most cases three files are used for a skim, prefixed with the starting date
of this skim in the [ISO format](http://en.wikipedia.org/wiki/ISO_8601)
which is denoted as `YYYY-MM-DD` in the following list.

1. A checkout recipe for additional CMSSW packages:
`checkoutXY.sh`

2. The CMSSW configuration file including the CMSSW version (XY) and a nick name:
`skim_XY_[name_]cfg.py

3. The grid-control configuration file are in the gc-cfg folder. They also mention
the responsible person of that skim in the form of initials (NN):
`YYYY-MM-DD_NN_XYZ_name.conf`

The skim is done by setting up CMSSW for skimming as described in the docs.
Then the relevant packages are checked out via the checkout script (1) and
the skim is run by running grid-control with the given configuration (3).