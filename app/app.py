#-*- coding: utf8 -*-

import sys
if sys.version_info[0] == 2:
    import Tkinter as tk
    import tkFileDialog as filedialog, tkMessageBox as messagebox
else:
    import tkinter as tk
    from tkinter import filedialog, messagebox
from subfinder.subfinder import SubFinder

class OutputStream():
    def __init__(self, text_widget):
        self.text = text_widget
    
    def write(self, text):
        self.text.insert(tk.END, text)
    
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
        subfinder = SubFinder(path=self.videofile, logger_output=self._output)
        subfinder.start()

    def _open_file(self):
        self._open('file')

    def _open_directory(self):
        self._open('dir')

    def _open(self, file_or_directory='file'):
        if file_or_directory == 'file':
            self.videofile = filedialog.askopenfilename(initialdir='~/Downloads/test',
                                                        filetypes=(
                                                            ('Video files', '*.mkv *.avi *.mp4 *'), ),
                                                        title="选择一个视频文件")
        elif file_or_directory == 'dir':
            self.videofile = filedialog.askdirectory(initialdir='~/Downloads/test',
                                                     title="选择一个目录")
        self.label_selected['text'] = self.videofile

    def _create_widgets(self):
        self.button_open_file = tk.Button(
            self, text='选择文件', command=self._open_file)
        self.button_open_file.grid(row=0, column=0, sticky='nswe')

        self.button_open_directory = tk.Button(
            self, text='选择目录', command=self._open_directory)
        self.button_open_directory.grid(row=0, column=1, sticky='nswe')

        frame = tk.Frame(self)
        self.label = tk.Label(frame, text='选中的文件或目录：')
        self.label.pack(side=tk.LEFT)
        self.label_selected = tk.Label(frame, text=self.videofile)
        self.label_selected.pack(side=tk.LEFT)
        frame.grid(row=1, column=0, columnspan=2, sticky='nswe')

        self.button_start = tk.Button(self, text='开始', command=self._start)
        self.button_start.grid(
            row=2, column=0, columnspan=2, pady=20, sticky='nswe')

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

        tk.Grid.rowconfigure(self, 3, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)


# window = tk.Tk()
app = Application()
app.mainloop()
