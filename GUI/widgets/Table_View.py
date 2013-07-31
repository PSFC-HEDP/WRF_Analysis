__author__ = 'Alex Zylstra'

try:
    import Tkinter
    import tkFont
except ImportError:
    import tkinter as Tkinter
    import tkinter.font as tkFont

import ttk

def sortby(tree, col, descending):
    """Sort tree contents when a column is clicked on."""
    # grab values to sort
    data = [(tree.set(child, col), child) for child in tree.get_children('')]

    # reorder data
    data.sort(reverse=descending)
    for indx, item in enumerate(data):
        tree.move(item[1], '', indx)

    # switch the heading so that it will sort in the opposite direction
    tree.heading(col,
        command=lambda col=col: sortby(tree, col, int(not descending)))

class Table_Viewer(Tkinter.Toplevel):
    """Implement a top-level window to display info in a tabular fashion. It's intended that this class is extended"""

    header_widgets = []  # control widgets to display at the top of the window
    tree_columns = ("Quantity", "Value")  # the column headings
    tree_data = [("",      "",)]  # the tree data

    def __init__(self, parent=None, build=True):
        """Initialize the table.
        :param parent: (optional) The parent of this window [default=None]
        :param build: (optional) Whether to call the widget building functions in the constructor [default=True]
        """
        super(Table_Viewer, self).__init__(parent)
        self.tree = None

        if build:
            self.__setup_widgets__()
            self.__build_tree__()

        self.protocol("WM_DELETE_WINDOW", self.withdraw)

    def __setup_widgets__(self):
        """Add the widgets and table to the GUI"""
        # add header widgets to the GUI:
        for widget in self.header_widgets:
            widget.pack()

        container = ttk.Frame(self)
        container.pack(fill='both', expand=True)

        # a treeview with scrollbars.
        self.tree = ttk.Treeview(container, columns=self.tree_columns, show="headings")
        vsb = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=container)
        vsb.grid(column=1, row=0, sticky='ns', in_=container)
        hsb.grid(column=0, row=1, sticky='ew', in_=container)

        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

    def __build_tree__(self):
        """Build the tree part of the widget"""
        # start by clearing everything already in the tree:
        map(self.tree.delete, self.tree.get_children())

        # add in new data:
        for col in self.tree_columns:
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: sortby(self.tree, c, 0))
            # set up with width based on font
            self.tree.column(col, width=tkFont.Font().measure(col.title()))

        for item in self.tree_data:
            self.tree.insert('', 'end', values=item)

            # adjust columns lengths if necessary
            for indx, val in enumerate(item):
                ilen = tkFont.Font().measure(val)
                if self.tree.column(self.tree_columns[indx], width=None) < ilen:
                    self.tree.column(self.tree_columns[indx], width=ilen)