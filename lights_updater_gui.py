#!/usr/bin/env python3
import tkinter
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

import sys
import subprocess
import threading


class StdOutRedirect:
    def __init__(self, widget: tkinter.Text):
        self.widget = widget

    def write(self, text: str):
        self.widget.after(0, self._write, text)

    def _write(self, text: str):
        self.widget.insert(tkinter.END, text)
        self.widget.yview(tkinter.END)  # type: ignore

    def flush(self):
        pass


class UpdaterGui:
    def __init__(self) -> None:
        self.config: dict[str, str] = {"csl_path": ""}

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
        self.root.minsize(400, 300)

        self.root.title("Lights updater for CSL objects")
        self.process_info_label = tkinter.Label(
            self.root, text="No processing running!", fg="blue", padx=5, pady=5
        )
        self.process_info_label.pack()
        if self.config["csl_path"] == "":
            self.selected_dir_label = tkinter.Label(
                self.root, text="CSL directory: not selected!", fg="red", padx=5, pady=5)
        else:
            self.selected_dir_label = tkinter.Label(
                self.root, text=f"CSL directory: {self.config['csl_path']}", fg="red", padx=5, pady=5)

        self.selected_dir_label.pack()

        self.output = ScrolledText(self.root)
        self.output.pack(padx=10, pady=10, expand=True,
                         fill=tkinter.BOTH, side=tkinter.LEFT)

        old_stdout = sys.stdout
        sys.stdout = StdOutRedirect(self.output)
        sys.stderr = StdOutRedirect(self.output)

        self.menu = tkinter.Menu(self.root)
        self.root.config(menu=self.menu)

        self.file_menu = tkinter.Menu(self.menu, tearoff=False)

        self.file_menu.add_command(
            label="Run 'normal' conversion", command=self.start_conversion)

        self.file_menu.add_command(
            label="Run conversion with flashing beacons",
            command=self.start_conversion_with_flashing_beacons
        )
        self.file_menu.add_command(
            label="Remove backup files", command=self.remove_backup_files
        )

        self.file_menu.add_command(
            label="Run undo", command=self.undo_conversion)

        self.file_menu.add_command(label="Exit", command=self.root.destroy)

        self.CSL_menu = tkinter.Menu(self.menu, tearoff=False)

        self.CSL_menu.add_command(
            label="Select CSL directory",
            command=self.set_csl_directory
        )

        self.help_menu = tkinter.Menu(self.menu, tearoff=False)
        self.help_menu.add_command(
            label="Show version", command=self.show_version
        )

        self.menu.add_cascade(
            label="File",
            menu=self.file_menu,
            underline=0
        )

        self.menu.add_cascade(
            label="CSL",
            menu=self.CSL_menu,
            underline=0
        )

        self.menu.add_cascade(
            label="Help",
            menu=self.help_menu,
            underline=0
        )

        self.root.mainloop()
        sys.stdout = old_stdout

    def run_process(self, cli_params: str, task: str) -> None:
        self.output.delete(1.0, tkinter.END)
        self.process_info_label.config(text=f"Processing...{task}", fg="blue")

        cmd = ["python3", "lights_updater.py", "-p",
               self.config["csl_path"], "--from_gui"]
        if cli_params:
            cmd.insert(-1, cli_params)

        def reader_thread():
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in iter(process.stdout.readline, ''):  # type: ignore
                print(line, end='')  # 'print' writes to redirected stdout
            process.stdout.close()  # type: ignore
            process.wait()
            print("Done!")

        threading.Thread(target=reader_thread, daemon=True).start()

    def start_conversion(self) -> None:
        if self.config["csl_path"] == "":
            messagebox.showerror(  # type: ignore
                "Error", "No CSL directory selected")
            return
        self.process_info_label.config(
            text="Run 'normal' conversion", fg="green")
        cli_params = ""
        self.run_process(cli_params, "standard conversion")

    def start_conversion_with_flashing_beacons(self) -> None:
        if self.config["csl_path"] == "":
            messagebox.showerror(  # type: ignore
                "Error", "No directory selected")
            return
        self.process_info_label.config(
            text="Run conversion with flashing beacons", fg="green")
        cli_params = "--flashing_beacons"
        self.run_process(cli_params, "conversion with flashing beacons")

    def remove_backup_files(self) -> None:
        if self.config["csl_path"] == "":
            messagebox.showerror(  # type: ignore
                "Error", "No CSL directory selected")
            return
        self.process_info_label.config(
            text="Removing backups. Be careful!", fg="green")
        answer = self.show_delete_backups_warning(
            "Warning", "You will delete all backups. Continue?")
        if answer:
            cli_params = "--remove-backups"
            self.run_process(cli_params, "removing backups")
        else:
            print("No backusp removed.", flush=True)
            return

    def undo_conversion(self):
        if self.config["csl_path"] == "":
            messagebox.showerror(  # type: ignore
                "Error", "No directory selected")
            return
        self.process_info_label.config(
            text="Undoing prior conversions", fg="green")
        cli_params = "-u"
        self.run_process(cli_params, "undoing prior conversions")

    def show_version(self) -> None:
        self.process_info_label.config(text="Programm version", fg="green")
        cli_params = "--version"
        self.run_process(cli_params, "get version")

    def set_csl_directory(self) -> None:
        csl_directory = filedialog.askdirectory(
            initialdir=self.config["csl_path"], title="Select CSL directory")

        if csl_directory:
            self.config["csl_path"] = csl_directory
            self.selected_dir_label.config(text=csl_directory, fg="green")

    def show_delete_backups_warning(self, title: str, message: str) -> bool:
        return messagebox.askyesno(title, message)  # type: ignore


if __name__ == "__main__":
    app = UpdaterGui()
    app.show_gui()
