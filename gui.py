import tkinter as tk
from pathlib import PurePath
from tkinter import filedialog as fd, ttk, scrolledtext, END, messagebox

from scraper import extract_ids, read_csv, main

LARGE_FONT = ('Verdana', 12)
ICON = 'icon.icns'
TITLE = 'ScraperApp'


class ScraperApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # TODO set icon
        tk.Tk.wm_title(self, TITLE)
        #tk.Tk.iconbitmap(self, bitmap=ICON)
        #self.geometry('300x150')
        self.minsize(380, 320)

        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        # contains the various pages that make up the GUI
        self.frames = {}

        # register all pages here
        for f in (InputPage, ConfigPage, PageTwo):
            frame = f(container, self)
            self.frames[f] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(InputPage)

    def show_frame(self, controller):
        """ Switches a new frame of the GUI into view. """
        frame = self.frames[controller]
        frame.tkraise()


class InputPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.filename = tk.StringVar(value='')
        self.path = None
        self.controller = controller
        self.save_loc = tk.StringVar(value='')

        # LF: Input Data
        lf_input = tk.LabelFrame(self, text='Choose data source')
        lf_input.pack(padx=15, pady=10, fill='both', expand='true')
        lf_input.grid_rowconfigure(2, weight=1)
        #lf.grid_columnconfigure(0, weight=1)
        lf_input.grid_columnconfigure(1, weight=1)

        # Radios
        self.radio = tk.IntVar()
        self.r1 = tk.Radiobutton(lf_input, text='Import CSV:', variable=self.radio, value=0)
        self.r2 = tk.Radiobutton(lf_input, text='Paste below:', variable=self.radio, value=1)

        self.r1.grid(row=0, column=0, ipady=5, padx=12, sticky='w')
        self.r2.grid(row=1, column=0, ipady=5, padx=12, sticky='w')

        open_csv_button = tk.Button(lf_input, text='Open CSV', command=self.select_file)
        open_csv_button.grid(row=0, column=1, padx=5, sticky='w')

        self.open_loc = tk.Label(lf_input, text=self.filename.get())
        self.open_loc.grid(row=0, column=2, sticky='e', padx=10)

        # Text Input
        txt = scrolledtext.ScrolledText(lf_input, width=50, height=8, wrap='word', borderwidth='2', relief='groove')
        txt.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky='nsew')

        # LF: Select Data
        lf_select = tk.LabelFrame(self, text='Select data to extract')
        lf_select.pack(padx=15, pady=10, fill='both', expand='false')
        lf_select.grid_columnconfigure(0, weight=1)
        lf_select.grid_columnconfigure(1, weight=1)
        lf_select.grid_columnconfigure(2, weight=1)

        # Checkboxes
        cbs = []
        cb_text = ['title', 'director', 'genre', 'year', 'synopsis', 'cast', 'country', 'language', 'runtime',
                   'IMDb score',
                   'imdb_id', 'url']

        cbs_per_row = 3
        for i, t in enumerate(cb_text):
            cb = tk.Checkbutton(lf_select, text=t)
            cbs.append(cb)
            cb.select()
            row, column = divmod(i, cbs_per_row)
            cbs[i].grid(row=row, column=column, sticky='w')

        # LF: Configure Data
        lf_config = tk.LabelFrame(self, text='Configure data')
        lf_config.pack(padx=15, pady=10, fill='both', expand='false')

        max_cast = tk.IntVar(lf_config, value=3)
        max_cast_sb = tk.Scale(lf_config, from_=1, to=9, variable=max_cast, label='Max cast:', orient='horizontal')
        max_cast_sb.pack(side='left', padx=5, pady=5, fill='both', expand='true')

        max_genres = tk.IntVar(lf_config, value=3)
        max_genres_sb = tk.Scale(lf_config, from_=1, to=9, variable=max_genres, label='Max genres:',
                                 orient='horizontal')
        max_genres_sb.pack(side='left', padx=5, pady=5, fill='both', expand='true')

        max_langs = tk.IntVar(lf_config, value=2)
        max_langs_sb = tk.Scale(lf_config, from_=1, to=9, variable=max_langs, label='Max languages:',
                                orient='horizontal')
        max_langs_sb.pack(side='left', padx=5, pady=5, fill='both', expand='true')

        max_countries = tk.IntVar(lf_config, value=3)
        max_countries_sb = tk.Scale(lf_config, from_=1, to=9, variable=max_countries, label='Max countries:',
                                    orient='horizontal')
        max_countries_sb.pack(side='left', padx=5, pady=5, fill='both', expand='true')

        # LF: Save Location
        lf_save = tk.LabelFrame(self, text='Set save location')
        lf_save.pack(padx=15, pady=10, fill='both', expand='false')

        tk.Button(lf_save, text='Choose...', command=self.get_save_path).pack(side='left')
        tk.Label(lf_save, textvariable=self.save_loc).pack(side='right')

        # Navigation Buttons
        buttons_frame = tk.Frame(self)
        buttons_frame.pack(padx=15, pady=10, fill='both', expand='false')

        self.reset_button = tk.Button(buttons_frame, text='Reset', command=lambda: self.reset(txt, cbs))
        self.reset_button.pack(side='left')

        self.extract_button = tk.Button(buttons_frame, text='Extract...', command=lambda: self.validate_input(self.path, txt))
        self.extract_button.pack(side='right')

    def select_file(self):
        filetypes = [('CSV files', '*.csv')]
        self.path = fd.askopenfilename(title='Open CSV', filetypes=filetypes)

        filename = PurePath(self.path).name
        self.filename.set(value=filename)
        print(self.filename.get())
        self.open_loc.config(text=self.filename.get())

        # ensure the relevant radio is selected
        self.r1.invoke()

        # can sort the state management later
        self.extract_button.config(state='normal')

    def validate_input(self, path, txt):
        """ Ensure that the user has submitted some data, if so, begin the processing. """
        # Text radio is selected
        if self.radio.get():
            ids = extract_ids(txt.get('1.0', 'end-1c'))
            self.process_ids(ids)

        # CSV radio is selected
        else:
            if path:
                ids = read_csv(path)
                self.process_ids(ids)
            else:
                messagebox.showwarning(title='No IMDb IDs', message='No CSV specified.', parent=self)

    def process_ids(self, ids):
        """ If potential IDs are submitted, process them. Else warn the user. """
        if ids:
            # TODO sort out specifying the fields
            fields = []
            save_path = self.save_loc.get()
            if not save_path:
                save_path = self.get_save_path()
            if save_path:
                main(ids, fields, save_path)
        else:
            messagebox.showwarning(title='No IMDb IDs', message='No potential IMDb IDs identified.', parent=self)

    def get_save_path(self):
        save_path = fd.asksaveasfilename()
        self.save_loc.set(save_path)
        return save_path

    def reset(self, textbox, cbs):
        """ Reset the page """
        # todo a better way to do this?
        print('clear')
        self.r1.invoke()
        self.filename.set('')
        self.open_loc.config(text=self.filename.get())
        self.path = None
        textbox.delete(1.0, END)
        self.extract_button.config(state='disabled')

        for cb in cbs:
            cb.select()

        #TODO reset the scales


class ConfigPage(tk.Frame):
    def __init__(self, parent, controller, **kw):
        super().__init__(parent)

        # LABELFRAME
        lf = tk.LabelFrame(self, text='Select data to extract')
        lf.pack(padx=15, pady=15, fill='both', expand='true')

        # Checkboxes
        cbs = []
        cb_text = ['title', 'director', 'genre', 'year', 'synopsis', 'cast', 'country', 'language', 'runtime', 'IMDb score',
              'imdb_id', 'url']

        cbs_per_row = 3
        for i, t in enumerate(cb_text):
            cb = tk.Checkbutton(lf, text=t)
            cbs.append(cb)
            cb.select()
            row, column = divmod(i, cbs_per_row)
            cbs[i].grid(row=row, column=column, sticky='w')

        lf_config = tk.LabelFrame(self, text='Configure the film data')
        lf_config.pack(padx=15, pady=15, fill='both', expand='true')

        max_cast = tk.IntVar(lf_config, value=3)
        max_cast_sb = tk.Scale(lf_config, from_=1, to=9, variable=max_cast, label='Max cast:', orient='horizontal')
        max_cast_sb.grid(row=0, column=0)

        max_genres = tk.IntVar(lf_config, value=3)
        max_genres_sb = tk.Scale(lf_config, from_=1, to=9, variable=max_genres, label='Max genres:', orient='horizontal')
        max_genres_sb.grid(row=0, column=1)

        max_langs = tk.IntVar(lf_config, value=2)
        max_langs_sb = tk.Scale(lf_config, from_=1, to=9, variable=max_langs, label='Max languages:',
                                 orient='horizontal')
        max_langs_sb.grid(row=0, column=2)

        max_countries = tk.IntVar(lf_config, value=3)
        max_countries_sb = tk.Scale(lf_config, from_=1, to=9, variable=max_countries, label='Max countries:',
                                 orient='horizontal')
        max_countries_sb.grid(row=0, column=3)

        # lower buttons, in their own frame
        buttons_frame = tk.Frame(lf)
        buttons_frame.grid(row=3, column=0, columnspan=3, sticky='nsew')

        self.back_button = tk.Button(buttons_frame, text='Back', command=lambda: controller.show_frame(InputPage))
        self.back_button.pack(side='left', padx=10, pady=10)

        self.extract_button = tk.Button(buttons_frame, text='Extract!', command=self.extract)
        self.extract_button.pack(side='right', padx=10, pady=10)

    def extract(self):
        print('Extract the data!')

    def save_file(self):
        filename = fd.asksaveasfilename(parent=self)
        print(filename)
        # run the export function here


# PLACEHOLDERS FOR FURTHER PAGES

class PageTwo(tk.Frame):
    def __init__(self, parent, controller, **kw):
        super().__init__(parent)
        label = tk.Label(self, text='Page Two', font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text='Back', command=lambda: controller.show_frame(InputPage))
        button1.pack()

        button2 = ttk.Button(self, text='Page One', command=lambda: controller.show_frame(ConfigPage))
        button2.pack()


class PageThree(tk.Frame):
    def __init__(self, parent, controller, **kw):
        super().__init__(parent)
        label = tk.Label(self, text='Page Three', font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text='Back', command=lambda: controller.show_frame(InputPage))
        button1.pack()

        button2 = ttk.Button(self, text='Page One', command=lambda: controller.show_frame(ConfigPage))
        button2.pack()


def some_func(p):
    print(p)

app = ScraperApp()
app.mainloop()
