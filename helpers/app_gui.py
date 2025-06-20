import tkinter
from tkinter import filedialog, messagebox

import sys
import subprocess
import threading


class StdOutRedirect:
    def __init__(self, widget: tkinter.Text):
        self.widget = widget

    def write(self, text: str):
        self.widget.insert(tkinter.END, text)
        # self.widget.see(tkinter.END)

    def flush(self):
        pass


class ConfigCreator:
    def __init__(self) -> None:
        self.config: dict[str, str] = {}

    def show_gui(self) -> None:
        self.root = tkinter.Tk()

        # Center it on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = 800
        height = 600
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        self.root.title("Lights updater for CSL objects")
        self.selected_dir_label = tkinter.Label(
            self.root, text="No directory selected")
        self.selected_dir_label.pack()

        self.output = tkinter.Text(self.root)
        self.output.pack(expand=True, fill=tkinter.BOTH)
        self.output.insert(tkinter.END, "Logs:\n")
        scrollbar = tkinter.Scrollbar(self.output, command=self.output.yview)
        self.output['yscrollcommand'] = scrollbar.set
        scrollbar.pack(side='right', fill='y')

        old_stdout = sys.stdout
        sys.stdout = StdOutRedirect(self.output)

        self.menu = tkinter.Menu(self.root)
        self.root.config(menu=self.menu)

        self.file_menu = tkinter.Menu(self.menu, tearoff=False)
        self.file_menu.add_command(
            label="Run conversion", command=self.run)
        self.file_menu.add_command(label="Exit", command=self.root.destroy)

        self.config_menu = tkinter.Menu(self.menu, tearoff=False)

        self.config_menu.add_command(
            label="Select CSL directory",
            command=self.set_csl_directory
        )

        self.menu.add_cascade(
            label="File",
            menu=self.file_menu,
            underline=0
        )

        self.menu.add_cascade(
            label="Config",
            menu=self.config_menu,
            underline=0
        )

        self.root.mainloop()
        sys.stdout = old_stdout

    def run(self) -> None:
        threading.Thread(target=self.run_undo).start()

    def run_undo(self):
        if "csl_path" in self.config:
            process = subprocess.Popen(
                f"python lights_updater.py --path {self.config['csl_path']} --undo".split(
                ),
                text=True, stdout=subprocess.PIPE, bufsize=1
            )
            while process.poll() is None:
                msg: str = process.stdout.readline().strip()
                print(msg)
        else:
            messagebox.showerror(  # type: ignore
                "Error", "No directory selected")

    def set_csl_directory(self) -> None:
        csl_directory = filedialog.askdirectory(initialdir=".")
        print(csl_directory)

        if csl_directory:
            self.config["csl_path"] = csl_directory
            self.selected_dir_label.config(text=csl_directory)
            # messagebox.showinfo(  # type: ignore
            #     "Success", f"CSL directory selected: {csl_directory}")


if __name__ == "__main__":
    app = ConfigCreator()
    app.show_gui()
