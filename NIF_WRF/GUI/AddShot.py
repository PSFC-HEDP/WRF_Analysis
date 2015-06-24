__author__ = 'Alex Zylstra'

import tkinter as tk
import tkinter.ttk as ttk
from NIF_WRF.DB import Database
from NIF_WRF.DB.Snout_DB import *
from NIF_WRF.GUI.SetupDB_Editor import *

class AddShot(tk.Toplevel):
    """A GUI routine for streamlining the process of adding a shot.

    :param parent: The parent UI element for this window
    """

    def __init__(self, parent=None):
        """Constructor"""
        super(AddShot, self).__init__(master=parent)
        # open the snout DB:
        self.snout_db = Snout_DB(Database.FILE)

        # create the UI elements
        self.__create_widgets__()

        self.title('Add a shot')
        self.minsize(width=400, height=200)
        self.configure(background='#eeeeee')

        # stretch the column to fill all space:
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)

        # a couple key bindings:
        self.bind('<Escape>', self.withdraw)
        self.protocol("WM_DELETE_WINDOW", self.withdraw)

    def __create_widgets__(self):
        """Create the UI elements"""
        # shot number:
        self.label1 = ttk.Label(self, text='Shot Num', background='#eeeeee')
        self.label1.grid(row=0, column=0)
        self.shot_num_var = tk.StringVar()
        self.shot_num = ttk.Entry(self, textvariable=self.shot_num_var, background='#eeeeee')
        self.shot_num.grid(row=0, column=1, columnspan=2)

        self.label0 = ttk.Label(self, text='Shot Name', background='#eeeeee')
        self.label0.grid(row=1, column=0)
        self.shot_name_var = tk.StringVar()
        self.shot_name = ttk.Entry(self, textvariable=self.shot_name_var, background='#eeeeee')
        self.shot_name.grid(row=1, column=1, columnspan=2)

        self.label0 = ttk.Label(self, text='Hohlraum Drawing', background='#eeeeee')
        self.label0.grid(row=2, column=0)
        self.hohl_draw_var = tk.StringVar()
        self.hohl_draw = ttk.Entry(self, textvariable=self.hohl_draw_var, background='#eeeeee')
        self.hohl_draw.grid(row=2, column=1, columnspan=2)

        ttk_sep_1 = ttk.Separator(self, orient="vertical")
        ttk_sep_1.grid(row=3, column=0, columnspan=3, sticky='ew')

        self.label2 = tk.Label(self, text='WRF Used:', background='#eeeeee')
        self.label2.grid(row=4, column=0)

        # add drop downs for WRF options:
        opts = ['', 'AAA10-108020-02', 'AAA10-108020-07', 'AAA10-108020-08', 'AAA10-108020-10', 'other']
        self.WRF_Info = []
        self.Snout_Info = []
        DIMs = ['0-0', '90-78']
        positions = 4
        for dim in range(len(DIMs)):
            # add a label for the DIM 'column'
            label = tk.Label(self, text=DIMs[dim], background='#eeeeee')
            label.grid(row=4, column=dim+1)

            # add the info for each position:
            for pos in range(1,positions+1):
                # add a label on the first iteration only:
                if dim == 0:
                    label2 = tk.Label(self, text='Pos '+str(pos), background='#eeeeee')
                    label2.grid(row=4+pos, column=0)

                # add a dropdown to select wedge type
                var = tk.StringVar()
                menu = tk.OptionMenu(self, var, *opts)
                menu.configure(background='#eeeeee')
                menu.configure(width=20)
                var.set(opts[0])
                menu.grid(row=4+pos, column=1+dim)
                menu.configure(takefocus='1')  # allow keyboard focus
                self.WRF_Info.append([DIMs[dim], pos, var, menu])

            # once per DIM, we need a drop-down for snout type
            snout_opts = self.snout_db.get_names()
            snout_var = tk.StringVar()
            snout = tk.OptionMenu(self, snout_var, *snout_opts)
            snout.configure(background='#eeeeee')
            snout.grid(row=9, column=1+dim)
            self.Snout_Info.append([DIMs[dim], snout_var, snout])

        self.label3 = tk.Label(self, text='Snout', background='#eeeeee')
        self.label3.grid(row=9, column=0)

        ttk_sep_2 = ttk.Separator(self, orient="vertical")
        ttk_sep_2.grid(row=10, column=0, columnspan=3, sticky='ew')

        # add buttons to both cancel and go
        self.cancel_button = ttk.Button(self, text='Cancel', command=self.withdraw, style='TButton')
        self.cancel_button.grid(row=11, column=0)
        self.go_button = ttk.Button(self, text='Submit', command=self.add_shot, style='TButton')
        self.go_button.grid(row=11, column=1, columnspan=2, sticky='s')

    def add_shot(self):
        """Script to generate calls to add shots."""
        # get the top-level info
        shot_num = self.shot_num_var.get()
        shot_name = self.shot_name_var.get()
        hohl_draw = self.hohl_draw_var.get()

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

                if label == 'hohl_drawing':
                    dialog.vars[i].set(hohl_draw)
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
                    if label == 'cr39_2_id' or label == 'cr39_3_id' or label == 'poly_1' or label == 'poly_2':
                        dialog.entries[i].configure(state='disabled')

                if row[2].get() == 'AAA10-108020-10':  # config w/ indium
                    if label == 'cr39_3_id' or label == 'poly_2':
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

        self.withdraw()