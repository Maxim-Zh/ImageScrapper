#! /usr/bin/env python3
import os
import shutil
import tkinter as tk
import webbrowser
import logging
import threading
import psutil
from scrapper import ImageScrapper
from tkinter import messagebox as mb
from loggers import error_log

"""
Handle keypress, click, other events
"""
SRC_DIR = os.path.dirname(__file__)  # executable path


class StartButton:
    """
    Handles start button
    """
    scrapper = None

    def __init__(self, master):
        #  GUI params
        self.master = master
        self.progressbar = None
        self.button = None

        # scrapper params
        self.search_engine = None
        self.query = None
        self.max_urls = None

    def search_and_download(self) -> None:
        """
        Initialize image search and download

        :return: None
        """
        if self.query != '' and self.max_urls != '' and not self.max_urls.isalpha():
            if self.search_engine == 'Google':
                self.progressbar.place(x=40, y=122)
                self.progressbar.start()
                StartButton.scrapper = ImageScrapper()
                StartButton.scrapper.scrape_google(query=self.query, max_urls=int(self.max_urls))
            if self.search_engine == 'Yandex':
                self.progressbar.place(x=40, y=122)
                self.progressbar.start()
                StartButton.scrapper = ImageScrapper()
                StartButton.scrapper.scrape_yandex(query=self.query, max_urls=int(self.max_urls))
            if self.search_engine != 'Google' and self.search_engine != 'Yandex':
                error_log.error(f'No such search engine {self.search_engine}\n')
                mb.showerror(title='Error', message=f'No such search engine {self.search_engine}!')
                return
            result = StartButton.scrapper.download_image()
            if result:
                if mb.askyesno(title='Success', message='Downloading complete. Open directory?'):
                    webbrowser.open(result)
                    self.progressbar.stop()
                    self.progressbar.place_forget()
                self.progressbar.stop()
                self.progressbar.place_forget()
            else:
                mb.showinfo(title='Info', message='No images found.')
                self.progressbar.stop()
                self.progressbar.place_forget()
        else:
            mb.showerror(title='Error', message='Invalid query and/or number!')

    def start_button(self, search_engine: str, query: str, max_urls: str, progressbar, button) -> None:
        """
        Gathers parameters from widgets and initializes thread and selenium webdriver

        :param search_engine: Google or Yandex
        :param query: What to search
        :param max_urls: Number of images to download
        :param progressbar: ttk.Progressbar() obj
        :param button: ttk.Button() obj

        :return: None
        """
        self.progressbar = progressbar
        self.button = button
        self.search_engine = search_engine
        self.query = query
        self.max_urls = max_urls
        self.button.config(text='Working')
        self.button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.search_and_download,
                                  daemon=True)
        thread.start()
        self.check_thread(master=self.master, thread=thread, button=self.button)

    def check_thread(self, master, thread, button) -> None:
        """
        Checks if thread is alive
        """
        if thread.is_alive():
            master.after(100, lambda: self.check_thread(master=master, thread=thread, button=button))
        else:
            button.config(text='Start')
            button.config(state=tk.NORMAL)


class CloseButton:
    """
    Handles close window button
    """
    def __init__(self, master):
        self.master = master

    def close_button(self) -> None:
        """
        Handles close window button, moves log files to Log dir if created

        :return: None
        """
        if mb.askokcancel(title='Quit', message='Do you want to quit?'):
            #  check if info_log files are even created
            if os.path.exists(os.path.join(SRC_DIR, 'info_log.log')):
                log_dir = os.path.join(SRC_DIR, 'Log')
                if not os.path.exists(log_dir):
                    os.mkdir(log_dir)
                logging.shutdown()
                #  if there is no log file in Log dir
                if not os.path.exists(os.path.join(SRC_DIR, 'Log', 'info_log.log')):
                    shutil.move(src=os.path.join(SRC_DIR, 'info_log.log'),
                                dst=os.path.join(SRC_DIR, 'Log', 'info_log.log'))
                else:
                    #  append new_log content to old_log content and removes new_log file
                    with open(file=os.path.join(SRC_DIR, 'info_log.log'), mode='r', encoding='UTF-8') as new_log, open(
                            file=os.path.join(SRC_DIR, 'Log', 'info_log.log'), mode='a', encoding='UTf-8') as old_log:
                        for line in new_log:
                            old_log.write(line)
                    os.remove(os.path.join(SRC_DIR, 'info_log.log'))
            #  check if error_log files are even created
            if os.path.exists(os.path.join(SRC_DIR, 'error_log.log')):
                log_dir = os.path.join(SRC_DIR, 'Log')
                if not os.path.exists(log_dir):
                    os.mkdir(log_dir)
                logging.shutdown()
                #  if there is no log file in Log dir
                if not os.path.exists(os.path.join(SRC_DIR, 'Log', 'error_log.log')):
                    shutil.move(src=os.path.join(SRC_DIR, 'error_log.log'),
                                dst=os.path.join(SRC_DIR, 'Log', 'error_log.log'))
                else:
                    #  append new_log content to old_log content and removes new_log file
                    with open(file=os.path.join(SRC_DIR, 'error_log.log'), mode='r', encoding='UTF-8') as new_log, open(
                            file=os.path.join(SRC_DIR, 'Log', 'error_log.log'), mode='a', encoding='UTf-8') as old_log:
                        for line in new_log:
                            old_log.write(line)
                    os.remove(os.path.join(SRC_DIR, 'error_log.log'))

            # in case of emergency closing GUI and selenium webdriver is still active
            process_set = {process.name().lower() for process in psutil.process_iter()}
            if 'chromedriver.exe' in process_set and isinstance(StartButton.scrapper, ImageScrapper):
                StartButton.scrapper.webdriver.quit()

            self.master.destroy()


class CreateToolTip:

    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind(sequence="<Enter>", func=self.tooltip_enter)
        self.widget.bind(sequence="<Leave>", func=self.tooltip_leave)

    def tooltip_enter(self, event) -> None:
        """
        Creates toplevel tooltip window when mouse hovers over widget

        :return: None
        """

        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() - 118
        y += self.widget.winfo_rooty() + 25

        # Creates a toplevel window
        self.tooltip_window = tk.Toplevel(self.widget)

        # Leaves only the label and removes the app window
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f'+{x}+{y}')
        tooltip = tk.Label(self.tooltip_window, text=self.text, justify='left',
                           background='white', relief='solid', borderwidth=1,
                           font=("Arial", "10", "normal"))
        tooltip.pack(ipadx=10)

    def tooltip_leave(self, event) -> None:
        """
        Removes tooltip window

        :param event:
        :return: None
        """
        if self.tooltip_window:
            self.tooltip_window.destroy()


def click_on_entry(entry) -> None:
    """
    Clears entry on click

    :param entry: tk.Entry() obj
    :return: None
    """
    content = entry.get()
    if content == 'Paste your query' or content == 'N':
        entry.delete(0, 'end')


def default_value_entry(entry) -> None:
    """
    Returns default value in entry field when focused out
    :param entry: tk.Entry() obj
    :return: None
    """
    content = entry.get()
    if content == '':
        if str(entry) == '.!mainframe.!entry':
            entry.insert(0, 'Paste your query')
        if str(entry) == '.!mainframe.!entry2':
            entry.insert(0, 'N')


def set_focus(event) -> None:
    """
    Set focus on clicked widgets

    :param event: event
    :return: None
    """
    event.widget.focus_set()
