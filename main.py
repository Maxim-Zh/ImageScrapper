#! /usr/bin/env python3
import tkinter as tk
from tkinter import ttk
from handlers import click_on_entry, set_focus, start_button

WINDOW_HEIGHT = 150
WINDOW_WIDTH = 320
SE_LIST = ['Website', 'Google', 'Yandex', ]


class MainWindow(tk.Tk):

    def __init__(self):
        super().__init__()
        self.ww = WINDOW_WIDTH
        self.wh = WINDOW_HEIGHT
        self.sw = self.winfo_screenwidth()
        self.sh = self.winfo_screenheight()

        # WINDOW
        self.title('Image Scrapper')
        self.geometry(f'{self.ww}x{self.wh}+{self.sw // 2 - self.ww // 2}+{self.sh // 2 - self.wh // 2}')
        self.resizable(False, False)
        # self.iconbitmap('images/')

        # MAIN FRAME
        self.main_frame = MainFrame(master=self, relief=tk.FLAT)
        self.main_frame.bind(sequence='<Button-1>',
                             func=lambda event: set_focus(event=event))


class MainFrame(tk.Frame):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.mf_opt_variable = tk.StringVar()  # store current option menu select
        self.place(x=0, y=0, relwidth=1, relheight=1)

        # MESSAGE
        self.mf_message = tk.Message(master=self,
                                     text='Search and saves image from website',
                                     font=('Arial', 14),
                                     justify='center',
                                     width=WINDOW_WIDTH)
        self.mf_message.place(y=5, relwidth=1, relheight=.5)
        self.mf_message.bind(sequence='<Button-1>',
                             func=lambda event: set_focus(event=event))

        # OPTION MENU
        self.mf_om = ttk.OptionMenu(self, self.mf_opt_variable, 'Where to search?', *SE_LIST)
        self.mf_om.place(x=10, y=70)

        # ENTRY
        self.mf_search_entry = ttk.Entry(master=self, justify='center')
        self.mf_search_entry.insert(0, 'What to search?')
        self.mf_search_entry.bind(sequence='<Button-1>',
                                  func=lambda event: click_on_entry(entry=self.mf_search_entry), add='+')
        self.mf_search_entry.bind(sequence='<Button-1>', func=lambda event: set_focus(event=event), add='+')
        self.mf_search_entry.place(x=10, y=93, relwidth=.5, relheight=.15, )

        self.mf_max_urls = ttk.Entry(master=self, justify='center')
        self.mf_max_urls.insert(0, 'N')
        self.mf_max_urls.bind(sequence='<Button-1>',
                              func=lambda event: click_on_entry(entry=self.mf_max_urls), add='+')
        self.mf_max_urls.bind(sequence='<Button-1>', func=lambda event: set_focus(event=event), add='+')
        self.mf_max_urls.place(x=171, y=93, relwidth=.16, relheight=.15)

        # BUTTON
        self.mf_button = ttk.Button(master=self, text='Start')
        self.mf_button.bind(sequence='<Button-1>',
                            func=lambda event: start_button(search_engine=self.mf_opt_variable.get(),
                                                            query=self.mf_search_entry.get(),
                                                            max_urls=self.mf_max_urls.get()), add='+')
        self.mf_button.bind(sequence='<Button-1>', func=lambda event: set_focus(event=event), add='+')
        self.mf_button.place(x=222, y=92)


if __name__ == '__main__':
    root = MainWindow()
    root.mainloop()
