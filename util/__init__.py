__author__ = 'Alex Zylstra'

import os
import sys
import inspect

# add the data directory to the system and OS paths:
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"SRIM")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)
    os.environ['SRIM_data'] = cmd_subfolder