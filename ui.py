import os
import platform
import subprocess
import tkinter as tk
from pathlib import PurePath
from tkinter import filedialog as fd, ttk, scrolledtext, END, messagebox

# Configure UI
LARGE_FONT = ('Verdana', 12)
ICON = 'icon.icns'
TITLE = 'ScraperApp'
CBS_PER_ROW = 3
SCALES_PER_ROW = 4


class ScraperUI(tk.Tk):
    def __init__(self, scraper):
        super().__init__()

        # Holds a reference to a Scraper object (the controller)
        self.scraper = scraper
        # TODO does this really need to be a stringvar
        self.save_path = tk.StringVar()

        # TODO set icon
        tk.Tk.wm_title(self, TITLE)
        self.minsize(380, 320)

        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        # contains the various pages that make up the GUI
        self.frames = {}

        # register all pages here
        for f in (InputPage, ProgressPage, PageTwo):
            frame = f(container, self)
            self.frames[f] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(InputPage)

    def show_frame(self, controller):
        """ Switches a new page of the GUI into view. """
        frame = self.frames[controller]
        frame.tkraise()

    def set_scraper(self, scraper):
        """ Connect the Scraper object to the UI. """
        self.scraper = scraper

    def alert_user(self, heading, txt):
        """ Display an alert to the user, invoked by the controller. """
        messagebox.showwarning(title=heading, message=txt, parent=self)

    def ask_to_save(self):
        save_path = fd.asksaveasfilename(defaultextension='.csv')
        if save_path:
            self.show_frame(ProgressPage)
            self.save_path.set(value=save_path)
        return save_path

    def set_progress_max(self, count):
        """ Set the maximum value of the progress bar using the count of IDs that are being fetched. """
        self.frames[ProgressPage].progress_bar['maximum'] = count

    def update_progress(self, title, valid=True):
        """ Communicate the progress being made to the User."""
        progress_bar = self.frames[ProgressPage].progress_bar
        progress_bar['value'] += 1

        if valid:
            response = f'Retrieved... {title}\n'
        else:
            response = f'Invalid IMDb ID: {title}\n'

        if progress_bar['value'] == progress_bar['maximum']:
            response += '\n...DONE!'
            #self.frames[ProgressPage].progress_label['text'] = 'All done!'
            self.frames[ProgressPage].open_button.pack(side='right')

        self.frames[ProgressPage].txt.insert(END, response)


class InputPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.open_path = None
        self.controller = controller
        self.field_configs = self.controller.scraper.get_field_configs()

        # LF: Input Data
        lf_input = tk.LabelFrame(self, text='Choose data source')
        lf_input.pack(padx=15, pady=10, fill='both', expand='true')
        lf_input.grid_rowconfigure(2, weight=1)
        #lf.grid_columnconfigure(0, weight=1)
        lf_input.grid_columnconfigure(1, weight=1)

        # Radios
        self.radio_var = tk.IntVar()
        self.radio_import = tk.Radiobutton(lf_input, text='Import CSV:', variable=self.radio_var, value=0)
        self.radio_paste = tk.Radiobutton(lf_input, text='Paste below:', variable=self.radio_var, value=1)

        self.radio_import.grid(row=0, column=0, ipady=5, padx=12, sticky='w')
        self.radio_paste.grid(row=1, column=0, ipady=5, padx=12, sticky='w')

        open_csv_button = tk.Button(lf_input, text='Open CSV', command=self.select_file)
        open_csv_button.grid(row=0, column=1, padx=5, sticky='w')

        self.open_path_label = tk.Label(lf_input)
        self.open_path_label.grid(row=0, column=2, sticky='e', padx=10)

        # Text Input
        text_box = scrolledtext.ScrolledText(lf_input, width=50, height=8, wrap='word', borderwidth='2', relief='groove')
        text_box.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky='nsew')

        # DYNAMIC UI ELEMENTS - Checkboxes and Scales
        #fields = self.controller.scraper.get_field_names()
        #scale_configs = self.controller.scraper.get_field_configs()

        # LF: Select Data (Checkboxes)
        lf_select = tk.LabelFrame(self, text='Select data to extract')
        lf_select.pack(padx=15, pady=10, fill='both', expand='false')
        for column in range(CBS_PER_ROW):
            lf_select.grid_columnconfigure(column, weight=1)

        cb_vals = []
        for i, t in enumerate(self.field_configs.keys()):
            var = tk.IntVar(value=1)
            cb_vals.append((t, var))
            cb = tk.Checkbutton(lf_select, text=t, variable=var)
            row, column = divmod(i, CBS_PER_ROW)
            cb.grid(row=row, column=column, sticky='w')

        # LF: Configure Data (Scales)
        lf_config = tk.LabelFrame(self, text='Configure data')
        lf_config.pack(padx=15, pady=10, fill='both', expand='false')
        for column in range(SCALES_PER_ROW):
            lf_config.grid_columnconfigure(column, weight=1)

        counter = 0
        scale_vals = {}
        for field, config in self.field_configs.items():
            if config:
                var = tk.IntVar(lf_config, value=config['default'])
                scale = tk.Scale(lf_config, from_=config['min'], to=config['max'], variable=var, label=config['label'], orient='horizontal')
                scale_vals[field] = var
                row, column = divmod(counter, SCALES_PER_ROW)
                scale.grid(row=row, column=column, sticky='ew', padx=5, pady=5)
                counter += 1

        # Navigation Buttons
        buttons_frame = tk.Frame(self)
        buttons_frame.pack(padx=15, pady=10, fill='both', expand='false')

        self.reset_button = tk.Button(buttons_frame, text='Reset', command=lambda: self.reset(text_box, cb_vals, scale_vals))
        self.reset_button.pack(side='left')

        self.cont_button = tk.Button(buttons_frame, text='Continue', command=lambda: self.cont(self.open_path, text_box, cb_vals, scale_vals))
        self.cont_button.pack(side='right')

    def select_file(self):
        filetypes = [('CSV files', '*.csv')]
        self.open_path = fd.askopenfilename(title='Open CSV', filetypes=filetypes)

        path_to_display = self.truncate_path(self.open_path)
        self.open_path_label.config(text=path_to_display)

        # ensure the relevant radio is selected
        self.radio_import.invoke()

    def truncate_path(self, path):
        """ Shorten the filename as necessary so it fits neatly within the UI. """
        max_length = 20
        stem = PurePath(path).stem
        if len(stem) > max_length:
            diff = len(stem) - max_length
            stem = f'{stem[:-diff]} [...] '

        return stem + PurePath(path).suffix

    def cont(self, path, text_box, cb_vals, scale_vals):
        """ Ensure that the user has submitted some data, if so, continue to the next step. """
        #TODO tidy this up, perhaps contain it as a request object

        data = None
        # check which checkboxes are ticked
        fields = [val[0] for val in cb_vals if val[1].get()]

        scales = {}
        for scale, val in scale_vals.items():
            scales[scale] = val.get()

        if self.radio_var.get():
            data = text_box.get('1.0', 'end-1c')
            self.controller.scraper.process(data, fields, scales)
        else:
            if path:
                self.controller.scraper.process(data, fields, scales, path)
            else:
                # TODO this alert should be triggered by controller
                self.controller.alert_user('No CSV specified.', 'No CSV specified.')

    def get_save_path(self):
        return fd.asksaveasfilename()

    def reset(self, textbox, cb_vals, scale_vals):
        """ Reset the UI back to its initial state, ready for the user to start over. """
        self.radio_import.invoke()
        self.open_path_label.config(text='')
        self.open_path = None
        textbox.delete(1.0, END)

        # Tick all the checkboxes
        for cb in cb_vals:
            cb[1].set(value=1)

        # Reset the scales back to the defaults
        for s, v in scale_vals.items():
            v.set(value=self.field_configs[s]['default'])


class ProgressPage(tk.Frame):
    def __init__(self, parent, controller, **kw):
        super().__init__(parent)
        self.controller = controller

        # LF: Progress
        lf_progress = tk.LabelFrame(self, text='Fetching data from IMDb... ')
        lf_progress.pack(padx=15, pady=15, fill='both', expand='true')

        # Progress bar
        self.progress_bar = ttk.Progressbar(lf_progress, orient='horizontal', mode='determinate')
        self.progress_bar.pack(padx=15, pady=15, fill='x', expand='false', side='top')

        # Textbox that visibly logs the progress
        self.txt = scrolledtext.ScrolledText(lf_progress, width=50, height=6, wrap='word', borderwidth='2',
                                             relief='groove')
        self.txt.pack(padx=15, pady=15, fill='both', expand='true')

        # Navigation Buttons
        buttons_frame = tk.Frame(self)
        buttons_frame.pack(padx=15, pady=10, fill='both', expand='false')

        self.back_button = tk.Button(buttons_frame, text='Back', command=self.back)
        self.back_button.pack(side='left')

        self.progress_label = tk.Label(buttons_frame, text='', font=LARGE_FONT)
        self.progress_label.pack(side='right')

        self.open_button = tk.Button(buttons_frame, text='Open Result...', command=self.open)

    def back(self):
        # TODO signal that the user intends to cancel
        print('Cancel!')
        self.progress_bar['value'] = 0
        self.txt.delete(1.0, END)
        self.controller.show_frame(InputPage)
        self.open_button.pack_forget()

    def open(self):
        """Open the file created by the application in the User's default application."""
        path = self.controller.save_path.get()
        if platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', path))
        elif platform.system() == 'Windows':  # Windows
            os.startfile(path)
        else:  # linux variants
            subprocess.call(('xdg-open', path))

        """if os.name == 'nt':
            os.startfile(path)
        else:
            subprocess.call(('open', path))"""


# PLACEHOLDERS FOR FURTHER PAGES

class PageTwo(tk.Frame):
    def __init__(self, parent, controller, **kw):
        super().__init__(parent)
        label = tk.Label(self, text='Page Two', font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text='Back', command=lambda: controller.show_frame(InputPage))
        button1.pack()

        button2 = ttk.Button(self, text='Page One', command=lambda: controller.show_frame(ProgressPage))
        button2.pack()


class PageThree(tk.Frame):
    def __init__(self, parent, controller, **kw):
        super().__init__(parent)
        label = tk.Label(self, text='Page Three', font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text='Back', command=lambda: controller.show_frame(InputPage))
        button1.pack()

        button2 = ttk.Button(self, text='Page One', command=lambda: controller.show_frame(ProgressPage))
        button2.pack()
