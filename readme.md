# WRF analysis

this code is meant to expedite the process of analyzing Wedge Range Filters (WRFs) for ICF implosions.
there is a GUI that lets you do a bunch of spectrum correction and analysis stuff,
and a script that takes a bunch of analysis files from the program Analyze CR39 an consolidates them into useful figures and tables.
installation is tricky, as this relies on the stopping power library that is hosted in the StopPow repository.
here are Graeme's instructions for installing on Linux:

-get gsl version 1.x (not 2.x)
    -./configure
    -make
    -make check
    -make install
-get swig (tested with v 3.something)
-get WRF_Analysis
-StopPow:
    -get stoppow from github
    -cd python_swig, make
    -move \_StopPow.so AND StopPow.py (from python_swig/dist) to WRF_Analysis/util/
-run WRF:
    -move main.py to WRF_Analysis-master (ie WRF_Analysis/../)
    -python3 main.py

this can also be run on Windows, but it's harder because the tools for compiling gsl aren't as readily available.
basically, instead of \_StopPow.so, you want to end up with the Windows verison, which is \_StopPow.lib, and which must be compiled in Windows.
I was abe to do this by getting GSL 1.x for Windows off the internet (I also had to find a copy of the GNU 1.16 source), compile that to a .def file (I didn't rite down how I did that, so maybe I just downloaded the .def file), and then compile that to the .lib using "Developer Command Prompt for VS 2019", which you may need to install (I think it comes with the Visual Studio compiler which I already had on my computer for some reason).
I didn't write down the exact command, but you can probably just google it, since I think that's what I did.

as a side note, I don't seem to have `_StopPow.lib` in my local copy of this repo but it still works, so idk what the deal with that is.
I do have `_StopPow.cp39-win_amd64.pyc`, so maybe that's a sufficient substitute for the .lib file.
but I really could have sworn I rememberd creating the .lib file.
maybe I deleted it... weerd.
