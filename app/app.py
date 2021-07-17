# -*- coding: utf8 -*-
import sys

import tkinter as tk
from tkinter import filedialog, messagebox
from queue import Queue, Empty
from threading import Thread
from subfinder.subfinder_thread import SubFinderThread as SubFinder
from subfinder.subsearcher import get_subsearcher
from subfinder.run_thread import run


class OutputStream:
    def __init__(self, text_widget):
        self.text = text_widget
        self.msg_queue = Queue(100)

    def display(self):
        while True:
            try:
                msg = self.msg_queue.get(block=False)
            except Empty:
                break
            else:
                self.text.configure(state='normal')
                self.text.insert(tk.END, msg)
                self.text.configure(state='disabled')
                self.text.yview(tk.END)

    def write(self, text):
        self.msg_queue.put(text)

    def writeline(self, line):
        self.write(line + '\n')

    def writelines(self, lines):
        for line in lines:
            self.writeline(line)

    def close(self):
        pass

    def flush(self):
        pass


class Application(tk.Frame, object):
    def __init__(self, master=None, cnf={}, **kw):
        super(Application, self).__init__(master, cnf, **kw)
        self.title = 'SubFinder'
        self.videofile = ''
        self._output = None

        # self.master.geometry('300x100')
        self.master.title(self.title)
        self.pack(fill=tk.BOTH, expand=tk.YES, padx=10, pady=10)

        self._create_widgets()

    def _start(self):
        if not self.videofile:
            messagebox.showwarning('提示', '请先选择视频文件或目录')
            return

        def start(*args, **kwargs):
            subfinder = SubFinder(*args, **kwargs)
            subfinder.start()
            subfinder.done()

        t = Thread(
            target=start,
            args=[
                self.videofile,
            ],
            kwargs=dict(logger_output=self._output),
        )
        t.start()

    def _open_file(self):
        self._open('file')

    def _open_directory(self):
        self._open('dir')

    def _open(self, file_or_directory='file'):
        if file_or_directory == 'file':
            self.videofile = filedialog.askopenfilename(
                initialdir='~/Downloads/test', filetypes=(('Video files', '*.mkv *.avi *.mp4 *'),), title="选择一个视频文件"
            )
        elif file_or_directory == 'dir':
            self.videofile = filedialog.askdirectory(initialdir='~/Downloads/test', title="选择一个目录")
        self.label_selected['text'] = self.videofile

    def _display_msg(self):
        self._output.display()
        self.after(100, self._display_msg)

    def _create_widgets(self):
        self.button_open_file = tk.Button(self, text='选择文件', command=self._open_file)
        self.button_open_file.grid(row=0, column=0, sticky='nswe')

        self.button_open_directory = tk.Button(self, text='选择目录', command=self._open_directory)
        self.button_open_directory.grid(row=0, column=1, sticky='nswe')

        frame = tk.Frame(self)
        self.label = tk.Label(frame, text='选中的文件或目录：')
        self.label.pack(side=tk.LEFT)
        self.label_selected = tk.Label(frame, text=self.videofile)
        self.label_selected.pack(side=tk.LEFT)
        frame.grid(row=1, column=0, columnspan=2, sticky='nswe')

        self.button_start = tk.Button(self, text='开始', command=self._start)
        self.button_start.grid(row=2, column=0, columnspan=2, pady=20, sticky='nswe')

        frame = tk.Frame(self)
        self.text_logger = tk.Text(frame)
        self.scrollbar = tk.Scrollbar(frame, command=self.text_logger.yview)
        self.text_logger.configure(yscrollcommand=self.scrollbar.set)
        self.text_logger.grid(row=0, column=0, sticky='nswe')
        self.scrollbar.grid(row=0, column=1, sticky='ns')
        tk.Grid.rowconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(frame, 0, weight=1)
        # tk.Grid.columnconfigure(frame, 1, weight=1)
        frame.grid(row=3, column=0, columnspan=2, pady=20, sticky='nswe')
        self._output = OutputStream(self.text_logger)
        self.after(100, self._display_msg)

        tk.Grid.rowconfigure(self, 3, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        run()
    else:
        app = Application()
        app.mainloop()
