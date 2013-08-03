__author__ = 'Alex Zylstra'

import tkinter as tk
import ttk
from DB import Database
from DB.Snout_DB import *
from GUI.SetupDB_Editor import *

class AddShot(tk.Toplevel):
    """A GUI routine for streamlining the process of adding a shot."""

    def __init__(self, parent=None):
        super(AddShot, self).__init__(master=parent)
        # open the snout DB:
        self.snout_db = Snout_DB(Database.FILE)

        # create the UI elements
        self.__create_widgets__()

        self.title('Add a shot')
        self.minsize(width=400, height=200)

        # stretch the column to fill all space:
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)

    def __create_widgets__(self):
        # shot number:
        self.label1 = tk.Label(self, text='Shot Num')
        self.label1.grid(row=0, column=0)
        self.shot_num_var = tk.StringVar()
        self.shot_num = tk.Entry(self, textvariable=self.shot_num_var)
        self.shot_num.grid(row=0, column=1, columnspan=2)

        self.label0 = tk.Label(self, text='Shot Name')
        self.label0.grid(row=1, column=0)
        self.shot_name_var = tk.StringVar()
        self.shot_name = tk.Entry(self, textvariable=self.shot_name_var)
        self.shot_name.grid(row=1, column=1, columnspan=2)

        ttk_sep_1 = ttk.Separator(self, orient="vertical")
        ttk_sep_1.grid(row=2, column=0, columnspan=3, sticky='ew')

        self.label2 = tk.Label(self, text='WRF Used:')
        self.label2.grid(row=3, column=0)

        # add drop downs for WRF options:
        opts = ['', 'AAA10-108020-02', 'AAA10-108020-07', 'AAA10-108020-08', 'AAA10-108020-10', 'other']
        self.WRF_Info = []
        self.Snout_Info = []
        DIMs = ['0-0', '90-78']
        positions = 4
        for dim in range(len(DIMs)):
            # add a label for the DIM 'column'
            label = tk.Label(self, text=DIMs[dim])
            label.grid(row=3, column=dim+1)

            # add the info for each position:
            for pos in range(1,positions+1):
                # add a label on the first iteration only:
                if dim == 0:
                    label2 = tk.Label(self, text='Pos '+str(pos))
                    label2.grid(row=3+pos, column=0)

                # add a dropdown to select wedge type
                var = tk.StringVar()
                menu = tk.OptionMenu(self, var, *opts)
                menu.configure(width=20)
                var.set(opts[0])
                menu.grid(row=3+pos, column=1+dim)
                menu.configure(takefocus='1')  # allow keyboard focus
                self.WRF_Info.append([DIMs[dim], pos, var, menu])

            # once per DIM, we need a drop-down for snout type
            snout_opts = self.snout_db.get_names()
            snout_var = tk.StringVar()
            snout = tk.OptionMenu(self, snout_var, *snout_opts)
            snout.grid(row=8, column=1+dim)
            self.Snout_Info.append([DIMs[dim], snout_var, snout])

        self.label3 = tk.Label(self, text='Snout')
        self.label3.grid(row=8, column=0)

        ttk_sep_2 = ttk.Separator(self, orient="vertical")
        ttk_sep_2.grid(row=9, column=0, columnspan=3, sticky='ew')

        # add buttons to both cancel and go
        self.cancel_button = tk.Button(self, text='Cancel', command=self.withdraw)
        self.cancel_button.grid(row=10, column=0)
        self.go_button = tk.Button(self, text='Submit', command=self.add_shot)
        self.go_button.grid(row=10, column=1, columnspan=2, sticky='s')

    def add_shot(self):
        """Script to generate calls to add shots."""
        # get the top-level info
        shot_num = self.shot_num_var.get()
        shot_name = self.shot_name_var.get()

        # remove unused rows:
        WRFs = []
        for row in self.WRF_Info:
            # if the selection is not empty, then we want it:
            if row[2].get() != '':
                WRFs.append(row)

        # for each of the modules, we need to launch a dialog
        for row in WRFs:
            # create the editor dialog:
            dialog = SetupDB_Editor()

            # figure out which snout:
            snout_name = ''
            for snout_row in self.Snout_Info:
                if snout_row[0] == row[0]:
                    snout_name = snout_row[1].get()

            # iterate over the rows of info in the editor:
            for i in range(len(dialog.labels)):
                label = dialog.labels[i].cget('text')
                # set all of the appropriate text boxes
                if label == 'shot':
                    dialog.vars[i].set(shot_num)
                    dialog.entries[i].configure(state='disabled')

                if label == 'wrf_type':
                    dialog.vars[i].set(row[2].get())
                    dialog.entries[i].configure(state='disabled')

                if label == 'shot_name':
                    dialog.vars[i].set(shot_name)
                    dialog.entries[i].configure(state='disabled')

                if label == 'dim':
                    dialog.vars[i].set(row[0])
                    dialog.entries[i].configure(state='disabled')

                if label == 'r':
                    try:
                        r = self.snout_db.query(snout_name, row[0], row[1])[0][5]
                        dialog.vars[i].set(str(r))
                        dialog.entries[i].configure(state='disabled')
                    except:
                        from tkinter.messagebox import showwarning
                        showwarning('Warning', 'Snout configuration not found', parent=self)

                if label == 'snout':
                    dialog.vars[i].set(snout_name)
                    dialog.entries[i].configure(state='disabled')

                if label == 'position':
                    dialog.vars[i].set(row[1])
                    dialog.entries[i].configure(state='disabled')

                # there are also text boxes that should be grayed out
                # for given wedge types:
                if row[2].get() == 'AAA10-108020-08':  # config w/o neutronics
                    if label == 'cr_39_2_id' or label == 'cr_39_3_id' or label == 'poly_1' or label == 'poly_2':
                        dialog.entries[i].configure(state='disabled')

                if row[2].get() == 'AAA10-108020-10':  # config w/ indium
                    if label == 'cr_39_3_id' or label == 'poly_2':
                        dialog.entries[i].configure(state='disabled')
                    if label == 'poly_1':  # 100um poly for this drawing
                        dialog.vars[i].set('100')
                        dialog.entries[i].configure(state='disabled')

                if row[2].get() == 'AAA10-108020-02' or row[2].get == 'AAA10-108020-07':
                    if label == 'poly_1':  # 100um poly for this drawing
                        dialog.vars[i].set('100')
                        dialog.entries[i].configure(state='disabled')
                    if label == 'poly_2':  # 100um poly for this drawing
                        dialog.vars[i].set('100')
                        dialog.entries[i].configure(state='disabled')
