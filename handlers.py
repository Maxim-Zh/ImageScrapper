#! /usr/bin/env python3
import webbrowser
from scrapper import SearchEngineImageScrapper
from tkinter import messagebox as mb
from loggers import error_log

"""
Handle keypress, click, other events
"""


def click_on_entry(entry):
    entry.delete(0, 'end')


def set_focus(event):
    event.widget.focus_set()
    print(event.widget.focus_get())
    return event.widget.focus_get()


def start_button(search_engine, query, max_urls):
    if query != '' and max_urls != '' and not max_urls.isalpha():
        try:
            scrapper = SearchEngineImageScrapper(search_engine=search_engine)
            scrapper.get_img_urls(query=query, max_urls=int(max_urls))
            result = scrapper.download_image()
            if result:
                if mb.askyesno(title='Success', message='Downloading complete. Open directory?'):
                    webbrowser.open(result)
        except KeyError as err:
            error_log.exception(f'No such search engine {search_engine} - {err}')
    else:
        mb.showerror(title='Error', message='Invalid query and/or number!')

