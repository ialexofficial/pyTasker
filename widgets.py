import pickle
from tkinter import Frame, Label, Menu, Button, Checkbutton, IntVar, Scrollbar, Canvas, Entry, Text, StringVar
from tkinter.constants import *
from tkinter.filedialog import asksaveasfile, askopenfile

class Task(Frame):
    def __init__(self, content, parent=None, key=None, current_task_var=None, font=('Roboto', 14, 'normal')):
        Frame.__init__(self, parent)
        self.pack(side=TOP, fill=X)
        self.font = font
        self.text = Button(
            self,
            text=content,
            command=lambda: self._set_current_task(key, current_task_var),
            font=self.font,
            borderwidth=0
        )
        self.var = IntVar()
        self.checkbox = Checkbutton(self, variable=self.var, command=self.refresh_task, font=self.font)
        self.checkbox.pack(side=LEFT, anchor=CENTER)
        self.text.pack(side=LEFT, anchor=CENTER, fill=BOTH)

    def _set_current_task(self, key, current_task_var):
        if key is not None and current_task_var is not None:
            current_task_var.set(key)

    def refresh_task(self):
        if self.var.get():
            self.text.config(font=(self.font[0], self.font[1], 'overstrike'))
        else:
            self.text.config(font=self.font)

class TaskList(Frame):
    def __init__(self, tasks, current_task, parent=None):
        Frame.__init__(self, parent)
        self.config(borderwidth=2, relief=GROOVE)
        self.pack(side=LEFT, fill=BOTH, expand=YES)
        Label(self, text='Your task list', font=('Roboto', 16, 'bold')).pack(side=TOP, anchor=CENTER, fill=X)
        canvas = Canvas(self, width=300, height=300, scrollregion=(0, 0, 300, 300))
        sbar = Scrollbar(self, command=canvas.yview)
        canvas.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        canvas.pack(fill=BOTH, expand=YES)
        self.list_frame = Frame(canvas)
        self.list_frame.pack(fill=BOTH, expand=YES)
        canvas.create_window(0, 0, anchor=NW, window=self.list_frame, width=300, height=300)
        self.tasks = tasks
        self.current_task = current_task
        self.make_tasks()

    def make_tasks(self):
        self.task_objs = {}
        for key, task in zip(self.tasks.keys(), self.tasks.values()):
            self.task_objs[key] = Task(task['preview'], parent=self.list_frame, key=key, current_task_var=self.current_task)
    def check_active_tasks(self, tasks):
        self.tasks = tasks
        for key, task in zip(self.tasks.keys(), self.tasks.values()):
            if key not in self.task_objs.keys():
                self.task_objs[key] = Task(task['preview'], parent=self.list_frame, key=key, current_task_var=self.current_task)
        clearing_list = []
        for key in self.task_objs.keys():
            if key not in self.tasks.keys():
                clearing_list.append(key)
        for key in clearing_list:
            self.task_objs[key].destroy()
            del self.task_objs[key]

class TaskContainer(Frame):
    def __init__(self, tasks, parent=None):
        Frame.__init__(self, parent)
        self.pack(fill=BOTH, expand=YES)
        self.tasks = tasks
        self.file = None
        self.menu = self.make_top_menu(parent)
        self.current_task = IntVar()
        self.current_task.trace('w', self._update_current_task)
        self.task_list = TaskList(tasks, self.current_task, parent=self)
        self.task_objs = self.task_list.task_objs
        self.task_manager = TaskManager(tasks, self.task_objs, self)
        self.task_manager.menu.task_adder.button.config(command=lambda: self.add_task())
        self.task_manager.menu.task_clear_or_delete_manager.clearing_button.config(command=lambda: self.clear_tasks())
        self.task_manager.menu.task_clear_or_delete_manager.deleting_button.config(command=lambda: self.delete_task())

    def _update_current_task(self, *options):
        current_task_key = self.current_task.get()
        for key, task in zip(self.task_objs, self.task_objs.values()):
            if(current_task_key == key):
                task.text.config(bg='#c9c9c9')
                self.task_manager.task_info.change_text(self.tasks[key]['main'])
            else:
                task.text.config(bg=self.cget('bg'))

    def make_top_menu(self, parent, create_new_file_bool=False):
        menu_root = Menu(parent)
        parent.config(menu=menu_root)

        def create_new_file(self):
            self.tasks = {}
            self.file = None
        def open_file(self):
            self.file = askopenfile(mode='rb+')
            self.tasks = pickle.load(self.file)
            self.clear_tasks()
        def save_file(self):
            if(self.file is None):
                self.file = asksaveasfile(mode='wb')
            self.file.seek(0)
            pickle.dump(self.tasks, self.file)
        def save_file_as(self):
            self.file = asksaveasfile(mode='wb')
            pickle.dump(self.tasks, self.file)

        file = Menu(menu_root)
        file.add_command(label='New file', command=lambda: create_new_file(self))
        file.add_command(label='Open file', command=lambda: open_file(self))
        file.add_command(label='Save file', command=lambda: save_file(self))
        file.add_command(label='Save file as ...', command=lambda: save_file_as(self))
        menu_root.add_cascade(label='File', menu=file)

    def add_task(self):
        self.task_manager.menu.task_adder.add_task(self.tasks)
        self.task_list.check_active_tasks(self.tasks)
    def clear_tasks(self):
        self.task_manager.menu.task_clear_or_delete_manager.clear_tasks(self.tasks, self.task_objs)
        self.task_list.check_active_tasks(self.tasks)
    def delete_task(self):
        key = self.task_list.current_task.get()
        if(key != 0):
            self.task_manager.menu.task_clear_or_delete_manager.delete_task(key, self.tasks, self.task_objs)
            self.task_manager.task_info.change_text('')
            self.task_list.check_active_tasks(self.tasks)

class TaskAdder(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack(side=TOP, fill=X)
        self.preview_text = StringVar()
        self.entry = Entry(self, textvariable=self.preview_text)
        self.entry.pack(side=TOP, fill=X)
        self.text = Text(self, height=10)
        self.text.pack(side=TOP, fill=X)
        self.button = Button(self, text='Add task')
        self.button.pack(side=TOP, anchor=CENTER, fill=X)

    def add_task(self, tasks):
        tasks[max(tasks.keys())+1] = {
            'preview': self.preview_text.get(),
            'main': self.text.get('1.0', END+'-1c')
        }
        self.entry.delete(0, END)
        self.text.delete('1.0', END)

class TaskClearOrDeleteManager(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack(side=TOP, fill=X)
        self.clearing_button, self.deleting_button = Button(self, text='Clear done tasks'), Button(self, text='Delete selected task')
        self.clearing_button.pack(side=LEFT, anchor=CENTER, fill=X, expand=YES)
        self.deleting_button.pack(side=RIGHT, anchor=CENTER, fill=X, expand=YES)

    def clear_tasks(self, tasks, task_objs):
        clearing_list = []
        for key, task in zip(task_objs, task_objs.values()):
            if task.var.get():
                clearing_list.append(key)
        for key in clearing_list:
            self.delete_task(key, tasks, task_objs)
    def delete_task(self, key, tasks, task_objs):
        task_objs[key].destroy()
        del task_objs[key]
        del tasks[key]

class TaskManagerMenu(Frame):
    def __init__(self, tasks, parent=None):
        Frame.__init__(self, parent)
        self.pack(side=TOP, anchor=CENTER, fill=X)
        self.task_adder = TaskAdder(parent=self)
        self.task_clear_or_delete_manager = TaskClearOrDeleteManager(parent=self)

class TaskMainInfo(Frame):
    def __init__(self, task=None, parent=None):
        Frame.__init__(self, parent)
        self.pack(side=TOP, fill=BOTH, expand=YES)
        Label(self, text='Task information', font=('Roboto', 16, 'bold')).pack(side=TOP, anchor=CENTER, fill=X)
        self.text = Text(self, font=('Roboto', 16, 'normal'))
        self.text.pack(side=TOP, anchor=CENTER, expand=YES, fill=BOTH)
    
    def change_text(self, text):
        self.text.delete('1.0', END)
        self.text.insert('1.0', text)

class TaskManager(Frame):
    def __init__(self, tasks, task_objs, parent=None):
        Frame.__init__(self, parent)
        self.config(borderwidth=2, relief=GROOVE)
        self.pack(side=RIGHT, fill=BOTH, expand=YES)
        Label(self, text='Task manager', font=('Roboto', 16, 'bold')).pack(side=TOP, anchor=N, fill=X)
        self.menu = TaskManagerMenu(tasks, self)
        self.task_info = TaskMainInfo(parent=self)