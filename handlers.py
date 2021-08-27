#! /usr/bin/env python3
import os
import shutil
import webbrowser
import logging
from scrapper import ImageScrapper
from tkinter import messagebox as mb
from loggers import error_log

"""
Handle keypress, click, other events
"""
SRC_DIR = os.path.dirname(__file__)  # executable path


def click_on_entry(entry) -> None:
    """
    Clears entry on click, preserves content

    :param entry: tk.Entry() obj
    :return: None
    """
    prev = entry.get()
    entry.delete(0, 'end')


def set_get_focus(event) -> str:
    """
    Set focus on clicked widgets and returns current focused widget

    :param event: event
    :return: str
    """
    event.widget.focus_set()
    print(str(event.widget.focus_get()))
    return str(event.widget.focus_get())


def start_button(search_engine: str, query: str, max_urls: str) -> None:
    """
    Initialize image search and download

    :param search_engine: Google, Yandex
    :param query: What to search
    :param max_urls: Number of images required
    :return: None
    """
    if query != '' and max_urls != '' and not max_urls.isalpha():
        try:
            scrapper = ImageScrapper()
            if search_engine == 'Google':
                scrapper.scrape_google(query=query, max_urls=int(max_urls))
            if search_engine == 'Yandex':
                scrapper.scrape_yandex(query=query, max_urls=int(max_urls))
            result = scrapper.download_image()
            if result:
                if mb.askyesno(title='Success', message='Downloading complete. Open directory?'):
                    webbrowser.open(result)
            else:
                mb.showinfo(title='Info', message='No images found.')
        except KeyError as err:
            error_log.exception(f'No such search engine {search_engine} - {err}\n')
            mb.showerror(title='Error', message=f'No such search engine {search_engine}!')
    else:
        mb.showerror(title='Error', message='Invalid query and/or number!')


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
