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
python convert_energy_to_rhoR.py ENERGY --shell_material=MATERIAL --shell_density=DENSITY --shell_temperature=TEMPERATURE [--secondary]
~~~
where `ENERGY` is that energy in MeV and
the remaining arguments describe the shell plasma conditions to assume.
you can also specify hohlraum parameters to automaticly apply a hohlraum correction.
call it with `-h` for more details; I don't want to get into it here.

if you're analyzing NIF data, there's a whole process.
it looks something like this:
1. manually download the traveler spreadsheet from the NIF programs server,
2. use `load_info_from_nif_database.py` to download the shot info and generate the etch/scan requests,
3. email Michelle and wait for her to process the CR39,
4. manually download the scan files from the NIF Archive Viewer,
5. use Fredrick’s *AnalyzeCR39* Windows application to infer the spectrum from the scan file,
6. optionally, use Patrick’s *[SecondaryAnalysis](https://github.com/PSFC-HEDP/SecondaryAnalysis)* Matlab repository to infer fuel ρR from yield ratios,
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

### other notes to organize later

for NIF shots you have to specify the hohlraum with a `hohlraum.txt` file.
it can be the thickness and material ("30μmAu") or multiple thicknesses and materials ("10Au 216Al")
or multiple lines of sight with multiple thicknesses and materials ("90-78 1: 10Au\\n90-78 4: 10Au 216Al\\n00-00:").
the hohlraum is always ignored on the polar DIM, so you usually don't need to specify the lines of sight.

NIF ablators are often doped with silicon or germanium or something.
the database won't volunteer that information, but you can look on the Archive.
I(Justin)'ve compared some analyses including or ignoring the doping,
and the difference is typically smaller than the errorbars,
so in general I don't think you should worry about it.
if the PI emails you and is like "what about the doping?" just say "no".

the plots and tables label the wedges with varying levels of specificity depending on how many different wedges are present.
so, for example, the shot number won't be listed on the x-axis if only one shot is being plotted,
because it would be redundant.
you don't generally need to worry about that,
but one rare edge case is where you want to analyze two or more parts of a WRF separately because of clipping or something.
what you can do then is analyze it multiple times with different area limits or whatever,
and distinguish the resulting analysis files by putting
"\_left\_", "\_right\_", "\_top\_", "\_bottom\_", "\_middle\_", and/or "\_full\_"
in the filenames.
the code will notice these tags and include them in the plots and tables to uniquely identify each analysis.

## Installation

you'll need the Python requirements, which are all on PyPI.
~~~bash
pip install -r requirements.txt
~~~

if you want to calculate ρRs, you'll also need the stopping power library that is hosted in the [StopPow](https://github.com/PSFC-HEDP/StopPow) repository.
this is where it gets tricky.
note that you can skip this part if you only want to make plots of the spectra.

here are Graeme's instructions for installing on Linux:

1. get gsl version 1.x (not 2.x)
    - `cd gsl`
    - `./configure`
    - `make`
    - `make check`
    - `make install`
3. get [SWIG](https://www.swig.org/download.html) (tested with v 3.something)
4. get [WRF_Analysis](https://github.com/PSFC-HEDP/WRF_Analysis)
5. StopPow:
    - get StopPow from GitHub
    - `cd StopPow/python_swig`
    - `make`
    - move `_StopPow.so` AND `StopPow.py` (from `StopPow/python_swig/dist/`) to `WRF_Analysis/src/`
6. run WRF:
    - this step was necessary for Graeme but not Joe so if you can't find `main.py` try just ignoring it.
    - move `main.py` to the root WRF_Analysis folder
    - `python3 main.py`

this can also be run on Windows, but it's harder because the tools for compiling gsl aren't as readily available.
basically, instead of `_StopPow.so`, you want to end up with the Windows verison,
which is `_StopPow.lib`, and which must be compiled in Windows.
I was abe to do this by getting GSL 1.x for Windows off the internet (I also had to find a copy of the GNU 1.16 source),
compile that to a .def file (I didn't rite down how I did that, so maybe I just downloaded the .def file),
and then compile that to the .lib using "Developer Command Prompt for VS 2019",
which you may need to install (I think it comes with the Visual Studio compiler which I already had on my computer for some reason).
I didn't write down the exact command, but you can probably just google it, since I think that's what I did.

as a side note, I don't seem to have `_StopPow.lib` in my local copy of this repo but it still works,
so idk what the deal with that is.
I do have `_StopPow.cp39-win_amd64.pyc` (which came from making in the `StopPow/python_swig/` folder),
so maybe that's a sufficient substitute for the .lib file.
but I really could have sworn I rememberd creating the .lib file.
How else would I have written the paragraph above this?
maybe I deleted it...
weerd.

### Running on WSL

If you're running on WSL, you might have difficulty working with the web-browser package.
This can be fixed by setting the `BROWSER` environment variable to your windows web-browser.
Here's an example:

   export BROWSER=/mnt/c/Program\ Files/Mozilla\ Firefox/firefox.exe

You'll probably need to modify this for your setup.
