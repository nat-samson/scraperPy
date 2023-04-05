import tkinter as tk
from pathlib import PurePath
from tkinter import filedialog as fd
from tkinter import ttk, scrolledtext, END

# configs
LARGE_FONT = ('Verdana', 12)
ICON = None  #'something.ico'
TITLE = 'ScraperApp'


class ScraperApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # TODO set icon
        tk.Tk.wm_title(self, TITLE)
        #tk.Tk.iconbitmap(self, default=ICON)
        #self.geometry('300x150')
        self.minsize(380, 320)

        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.frames = {}

        # register all pages here
        for f in (StartPage, PageOne, PageTwo):
            frame = f(container, self)
            self.frames[f] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(StartPage)

    def show_frame(self, controller):
        frame = self.frames[controller]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.filename = tk.StringVar(value='')
        self.path = None

        # LABELFRAME
        lf = tk.LabelFrame(self, text='Choose data source')
        lf.pack(padx=15, pady=15, fill='both', expand='true')
        lf.grid_rowconfigure(2, weight=1)
        #lf.grid_columnconfigure(0, weight=1)
        lf.grid_columnconfigure(1, weight=1)

        # RADIOS
        self.radio = tk.IntVar()
        self.r1 = tk.Radiobutton(lf, text='Import CSV:', variable=self.radio, value=0)
        self.r2 = tk.Radiobutton(lf, text='Paste below:', variable=self.radio, value=1)

        self.r1.grid(row=0, column=0, ipady=5, padx=12, sticky='w')
        self.r2.grid(row=1, column=0, ipady=5, padx=12, sticky='w')

        open_csv_button = tk.Button(lf, text='Open CSV', command=self.select_file)
        open_csv_button.grid(row=0, column=1, padx=5, sticky='w')

        self.label2 = tk.Label(lf, text=self.filename.get())
        self.label2.grid(row=0, column=2, sticky='e', padx=10)

        # text input
        txt = scrolledtext.ScrolledText(lf, width=50, height=10, wrap='word', borderwidth='2', relief='groove')
        txt.grid(row=2, column=0, columnspan=3, padx=10, sticky='nsew')

        # lower buttons, in their own frame
        buttons_frame = tk.Frame(lf)
        buttons_frame.grid(row=3, column=0, columnspan=3, sticky='nsew')

        self.clear_button = tk.Button(buttons_frame, text='Clear', command=lambda: self.clear(txt))
        self.clear_button.pack(side='left', padx=10, pady=10)

        self.cont_button = tk.Button(buttons_frame, text='Continue', command=lambda: self.cont_check(self.path, txt))
        self.cont_button.pack(side='right', padx=10, pady=10)

    def select_file(self):
        filetypes = [('CSV files', '*.csv')]
        self.path = fd.askopenfilename(title='Open CSV', filetypes=filetypes)

        filename = PurePath(self.path).name
        self.filename.set(value=filename)
        print(self.filename.get())
        self.label2.config(text=self.filename.get())

        # ensure the relevant radio is selected
        self.r1.invoke()

        # can sort the state management later
        self.cont_button.config(state='normal')

    def cont_check(self, path, txt):
        # pastebox is selected
        if self.radio.get():
            if txt.compare("end-1c", "==", "1.0"):
                print('No text provided!')
            else:
                print('Processing the text!')
                # function to check there is at least one possible IMDBid, if so proceed.
        # open csv is selected
        else:
            if path:
                print('Opening', path)
                # run same function as above
            else:
                print('No file is set!')


    def clear(self, textbox):
        """ Reset the page """
        print('clear')
        self.r1.invoke()
        self.filename.set('')
        # todo a better way to do this?
        self.label2.config(text=self.filename.get())
        self.path = None
        textbox.delete(1.0, END)


# PLACEHOLDERS FOR FURTHER PAGES

class PageOne(tk.Frame):
    def __init__(self, parent, controller, **kw):
        super().__init__(parent)
        label = tk.Label(self, text='Page One', font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text='Back', command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = ttk.Button(self, text='Page Two', command=lambda: controller.show_frame(PageTwo))
        button2.pack()


class PageTwo(tk.Frame):
    def __init__(self, parent, controller, **kw):
        super().__init__(parent)
        label = tk.Label(self, text='Page Two', font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text='Back', command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = ttk.Button(self, text='Page One', command=lambda: controller.show_frame(PageOne))
        button2.pack()


class PageThree(tk.Frame):
    def __init__(self, parent, controller, **kw):
        super().__init__(parent)
        label = tk.Label(self, text='Page Three', font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text='Back', command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = ttk.Button(self, text='Page One', command=lambda: controller.show_frame(PageOne))
        button2.pack()


def some_func(p):
    print(p)

app = ScraperApp()
app.mainloop()
