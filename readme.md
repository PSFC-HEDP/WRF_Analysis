# WRF analysis

this code is meant to expedite the process of analyzing Wedge Range Filters (WRFs) for ICF implosions.

## Using the code

if you're analyzing NIF data, there's a whole process.
it looks something like this:
1. download the traveler spreadsheet from the NIF programs server,
2. use `load_info_from_nif_database.py` to download the shot info and generate the etch/scan requests,
3. email Michelle and wait for her to process the CR39,
4. download the scan files from the NIF Archive Viewer,
5. use Fredrick’s *AnalyzeCR39* Windows application to infer the spectrum from the scan file,
6. optionally, use Patrick’s *[SecondaryAnalysis](https://github.com/PSFC-HEDP/SecondaryAnalysis)* Matlab repository to infer fuel ρR from yield ratios,
7. use `make_plots_from_analysis.py` to infer total ρR from mean energy and compile the spectra into plots and tables, and
8. use Google Slides or maybe LaTeX to compile those plots and tables into a document and send it to the PI.
9. upload the result reports to the shot dashboard on the NIF archive.

if it's OMEGA data, the process is similar.
instead of steps 1 and 2, get all the relevant info from OmegaOps,
and instead of emailing Michelle, email one of the other etch/scan labs.

more integration would definitely be beneficial.
in particular, it would be nice to have step 6 be part of this repository as well.
if you're reading this, maybe you can do that.
I bet 8 could be done in Python also, but it might be hard to make it look good.

anyway, I'll now describe the steps related to this repo in more detail.

### 2 – loading info from the NIF database

the script `load_info_from_nif_database.py` will retrieve and process basic shot information from WebDAV and any
traveller spreadsheets it can find and automaticly generate multiple files.

before calling this script you must be on the LLNL VPN and have created a subfolder for the relevant shot in `data/`.
that subfolder must have the shot's six- or nine-digit N number in the name (with or without the "-999"),
but it can also have other stuff (like you can name the folder "N231227 I_MJDD_PDD_WF" and that's fine).
you must also download the traveler spreadsheet(s) for the shot and put them in that folder.
they can be in subfolders (like if you want to have a subfolder for each line of sight) and that's fine.

when you call the script, you often only need to supply the shot's N number,
but there are a few other optional arguments:
~~~
python load_info_from_nif_database.py SHOT_NUMBER [--DD_yield=DD_YIELD --DD_temperature=DD_TEMPERATURE] [--downloads=DOWNLOADS]
~~~

`SHOT_NUMBER` can be the full twelve digits (like N210808-001-999),
but the "-999" can always be omitted,
and if it's the only shot on that particular date the "-001" can also be omitted.

this script will query WebDAV to get the nToF-measured DD yield and ion temperature,
which it uses to estimate the D³He yield.
however, it takes some time for the nToF people to authorize values,
so often when you're trying to compose etch requests there's no yield or ion temperature on WebDAV yet.
when that happens you can find the unauthorized nToF values on the NIF Archive
and pass them to the Python script using `DD_YIELD` (scientific notation is okay) and `DD_TEMPERATURE` (in keV).

if you're running on a weird platform like OSX or you've done something else weird to your computer,
this script might fail to find your downloads folder.
that's a problem because the way it queries WebDAV is by asking your default browser to download a bunch of CSV files and then reading them off your disk.
if it can't find those files, just find out where downloaded files actually go pass that directory as `DOWNLOADS` (environment variables are okay).

if you do all that correctly, it should add a row to `shot_info.csv` for this shot with the PI's name, the capsule parameters, and varius other things.
it will also create a file called `aux_info.csv` in the shot's folder listing the auxiliary diagnostics that were fielded
along with their filter and detector IDs and their exact coordinates in the target chamber.
finally, it will generate an etching and scanning workorder in the shot's folder that you can send to Michelle.

### 7 – making plots from the analysis

the script `make_plots_from_analysis.py` will take completed analysis and apply corrections for the hohlraum thickness,
infer ρR from the spectrum's mean energy, and consolidate all those numbers into nice plots and reports.
it's pretty robust compared to `load_info_from_nif_database.py` in that it doesn't need access to the database or to `aux_info.csv`;
it'll just run on any analysis file it finds.

before calling this script you must have analyzed all the CPSA files with AnalyzeCR39 and put the analysis CSVs in the shot's folder
(AnalyzeCR39 automaticly puts the analysis CSVs in the same folder as the CPSA files).
if it's a NIF shot you must also fill out a `hohlraum.txt` file in the shot's folder (you may also do this for OMEGA shots but it's not mandatory).
this will provide information about the hohlraum (which is not available on WebDAV for some reason)
and can also include varius flags to apply to the different lines of sight.

the simplest `hohlraum.txt` is the word "none", which will tell it that there was no hohlraum.
if there was a hohlraum, you can give the thickness and material ("8μmAu" or "8umAu" or "8Au") or multiple thicknesses and materials ("8Au 216Al").
see `tables/stopping_power_protons_*` for the list of valid materials.
if multiple lines of sight saw different things, you can put them on multiple lines like so:

> 90-78 1: 8Au  
> 90-78 4: 8Au 216Au  
> 00-00:

if any of the lines of sight had a clipped spectrum (as in you don't see the whole thing because it falls partially below 5 MeV),
you can also specify that in `hohlraum.txt` by adding "(clipped)" to the appropriate line.
this will let the Python script know that the inferred yield is only a lower bound and the inferred energy is only an upper bound.
similarly if any of them suffered from track-overlap you can add "(overlapped)" to the appropriate line
to let the script know that the inferred yield is only a lower bound.

if you used Patrick's secondary analysis code to get fuel ρRs, you can also put those numbers in `secondary_stuff.txt`.

when you call the script, you basicly only need the folder name if it's a NIF shot or if you don't care about ρR,
but you need to supply a bunch of additional information to get ρR for an OMEGA shot.
~~~
python make_plots_from_analysis.py "FOLDERS" [--shell_material=MATERIAL --shell_density=DENSITY --shell_temperature=TEMPERATURE [--secondary]] [--show]
~~~

you can pass multiple folders by making `FOLDERS` a comma-separated list,
and it will consolidate all the spectra in those folders in the same set of plots.
unfortunately unlike in step 2 you must pass the full name of the folder and not just the shot's N number.

if it's a NIF shot, it will use the info in `shot_info.csv` along with Alex's geometric implosion model to infer ρR.
if it's an OMEGA shot, that information is not available, so you'll need to specify shell conditions.
I recommend running a LILAC simulation to identify reasonable values.
the `MATERIAL` can be "CH", "CH2", "HDC", "SiO2", or "Be".
the `DENSITY` should be given in g/cm³, and the `TEMPERATURE` is the electron temperature in keV.
the calculation it then does is much simpler than for NIF shots;
it assumes a uniform shell plasma of the given conditions and calculates how thick it would have to be.
if it's a pure D implosion, make sure to add the `--secondary` flag to tell it to use a mean birth energy of 15.0 MeV instead of 14.7 MeV.

if you want you can also include `--show` to display the plots on the screen.
by default it just saves them to the first folder that was passed without showing them.

after the script runs, there will be a `wrf_analysis.csv` file in the folder that summarizes all of the key results and inferences in one place.
the yields, mean energies, and ρRs calculated from the shock peak will also be printed to the console.
the spectra themselves will be consolidated in `WRF spectra.xlsx` as well as in individual CSV files whose filenames start with "spectrum".
there will also be some report spreadsheets in each folder for each line of sight to be uploaded to the NIF Archive.
note that the Archive won't accept automaticly generated reports,
so you must open each one in Microsoft Excel and press save before uploading it.
finally, there will also be many plots. peruse them at your leisure.

### 10? – estimating other ρRs

sometimes you'll want to do some very rough analysis without having all the information,
or you may want to infer ρRs from some hypothetical mean energies.
in that case, there's a handy lightweight script that just calls the ρR part of the code:
~~~
python convert_energy_to_rhoR.py ENERGY --shell_material=MATERIAL --shell_density=DENSITY --shell_temperature=TEMPERATURE [--secondary]
~~~
where `ENERGY` is either the energy in MeV or the name of a file that contains multiple energies in MeV.
if you pass a file, you can also use include error bars by passing a file with two columns.
you can even use asymmetric error bars!
just pass a file with three columns (mean energy, lower uncertainty, upper uncertainty).

the remaining arguments describe the shell plasma conditions to assume.
you can also specify hohlraum parameters to automaticly apply a hohlraum correction.
call it with `--help` for more details; I don't want to get into it here.

### other notes to organize later

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
2. get [SWIG](https://www.swig.org/download.html) (tested with v 3.something)
3. get [WRF_Analysis](https://github.com/PSFC-HEDP/WRF_Analysis)
4. StopPow:
    - get StopPow from GitHub
    - `cd StopPow/python_swig`
    - `make`
    - move `_StopPow.so` AND `StopPow.py` (from `StopPow/python_swig/dist/`) to `WRF_Analysis/src/`
5. run WRF:
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
