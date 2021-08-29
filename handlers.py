#! /usr/bin/env python3
import os
import shutil
import tkinter as tk
import webbrowser
import logging
import threading
from scrapper import ImageScrapper
from tkinter import messagebox as mb
from loggers import error_log

"""
Handle keypress, click, other events
"""
SRC_DIR = os.path.dirname(__file__)  # executable path


def click_on_entry(entry) -> None:
    """
    Clears entry on click

    :param entry: tk.Entry() obj
    :return: None
    """
    content = entry.get()
    if content == 'Paste your search' or content == 'N':
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
            entry.insert(0, 'Paste your search')
        if str(entry) == '.!mainframe.!entry2':
            entry.insert(0, 'N')


def set_focus(event) -> None:
    """
    Set focus on clicked widgets

    :param event: event
    :return: None
    """
    event.widget.focus_set()


def search_and_download(search_engine: str, query: str, max_urls: str, progressbar) -> None:
    """
    Initialize image search and download

    :param search_engine: Google, Yandex
    :param query: What to search
    :param max_urls: Number of images required
    :param progressbar: tk.Progressbar() obj
    :return: None
    """
    if query != '' and max_urls != '' and not max_urls.isalpha():
        scrapper = ImageScrapper()
        if search_engine == 'Google':
            progressbar.place(x=40, y=122)
            progressbar.start()
            scrapper.scrape_google(query=query, max_urls=int(max_urls))
        if search_engine == 'Yandex':
            progressbar.place(x=40, y=122)
            progressbar.start()
            scrapper.scrape_yandex(query=query, max_urls=int(max_urls))
        if search_engine != 'Google' and search_engine != 'Yandex':
            error_log.exception(f'No such search engine {search_engine}\n')
            mb.showerror(title='Error', message=f'No such search engine {search_engine}!')
        result = scrapper.download_image()
        if result and result[1] != 0:
            if mb.askyesno(title='Success', message='Downloading complete. Open directory?'):
                webbrowser.open(result[0])
                progressbar.stop()
                progressbar.place_forget()
            progressbar.stop()
            progressbar.place_forget()
        else:
            mb.showinfo(title='Info', message='No images found.')
            progressbar.stop()
            progressbar.place_forget()
    else:
        mb.showerror(title='Error', message='Invalid query and/or number!')


def start_button(master, search_engine: str, query: str, max_urls: str, progressbar, button):
    button.config(state=tk.DISABLED)
    thread = threading.Thread(target=search_and_download,
                              args=(search_engine, query, max_urls, progressbar),
                              daemon=True)
    thread.start()
    check_thread(master=master, thread=thread, button=button)


def check_thread(master, thread, button):
    if thread.is_alive():
        master.after(100, lambda: check_thread(master=master, thread=thread, button=button))
    else:
        button.config(state=tk.NORMAL)


def on_closing(master) -> None:
    """
    Handles close window button, moves log files to Log dir if created

    :param master: tk.Tk() obj
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

        master.destroy()
