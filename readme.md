# WRF analysis

this code is meant to expedite the process of analyzing Wedge Range Filters (WRFs) for ICF implosions.

## Using the code

there are three executable Python scripts here:
- convert_energy_to_rhoR.py
- load_info_from_nif_database.py
- make_plots_from_analysis.py

the first one is very simple.
if you have a mean energy and want to know to what ρR it corresponds, just do
~~~bash
python convert_energy_to_rhoR.py ENERGY MATERIAL
~~~
where `ENERGY` is that energy in MeV and `MATERIAL` is the ablator material.
you can also specify hohlraum parameters to automaticly apply a hohlraum correction.
call it with `-h` for the full syntax; I don't want to get into it here.

if you're analyzing NIF data, there's a whole process.
it looks something like this:
1. manually download the traveler spreadsheet from the NIF programs server,
2. use `load_info_from_nif_database.py` to download the shot info and generate the etch/scan requests,
3. email Michelle and wait for her to process the CR39,
4. manually download the scan files from the NIF Archive Viewer,
5. use Fredrick’s *AnalyzeCR39* Windows application to infer the spectrum from the scan file,
6. optionally, use Patrick’s *SecondaryAnalysis* Matlab repository to infer fuel ρR from yield ratios,
7. use `make_plots_from_analysis.py` to infer total ρR from mean energy and compile the spectra into plots and tables, and
8. use Google Slides or maybe LaTeX to compile those plots and tables into a document and send it to the PI.

if it's OMEGA data, the process is similar.
instead of steps 1 and 2, get all the relevant info from OmegaOps,
and instead of emailing Michelle, email one of the other etch/scan labs.

more integration would definitely be beneficial.
in particular, it would be nice to have step 6 be part of this repository as well.
if you're reading this, maybe you can do that.
I bet 8 could be done in Python also, but it might be hard to make it look good.

anyway, I'll probably add more specific instructions about each of these steps later.
for now, just call the python scripts with `-h` and that will tell you what you need to know.

## Installation

you'll need the Python requirements, which are all on PyPI.
~~~bash
pip install -r requirements.txt
~~~

you'll also need the stopping power library that is hosted in the StopPow repository.
this is where it gets tricky.
here are Graeme's instructions for installing on Linux:

1. get gsl version 1.x (not 2.x)
    - ./configure
    - make
    - make check
    - make install
2. get swig (tested with v 3.something)
3. get WRF_Analysis
4. StopPow:
    - get stoppow from github
    - cd python_swig, make
    - move \_StopPow.so AND StopPow.py (from python_swig/dist) to src/
5. run WRF:
    - move main.py to WRF_Analysis-master (ie src/../)
    - python3 main.py

this can also be run on Windows, but it's harder because the tools for compiling gsl aren't as readily available.
basically, instead of \_StopPow.so, you want to end up with the Windows verison,
which is \_StopPow.lib, and which must be compiled in Windows.
I was abe to do this by getting GSL 1.x for Windows off the internet (I also had to find a copy of the GNU 1.16 source),
compile that to a .def file (I didn't rite down how I did that, so maybe I just downloaded the .def file),
and then compile that to the .lib using "Developer Command Prompt for VS 2019",
which you may need to install (I think it comes with the Visual Studio compiler which I already had on my computer for some reason).
I didn't write down the exact command, but you can probably just google it, since I think that's what I did.

as a side note, I don't seem to have `_StopPow.lib` in my local copy of this repo but it still works,
so idk what the deal with that is.
I do have `_StopPow.cp39-win_amd64.pyc` (which came from making in the python_swig folder),
so maybe that's a sufficient substitute for the .lib file.
but I really could have sworn I rememberd creating the .lib file.
How else would I have written the paragraph above this?
maybe I deleted it...
weerd.
