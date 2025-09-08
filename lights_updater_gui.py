#!/usr/bin/env python3
import json
import tkinter
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

import os
import sys
import platform
import subprocess
import threading
import shlex
from typing import Any


class StdOutRedirect:
    """Class to redirect stdout
    """

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
    """
    The code behind the GUI. Finally lights_updater is clickable!
    """

    def __init__(self, config: dict[str, Any], config_file: str) -> None:
        self.config = config
        self.config_file = config_file
        self.process: subprocess.Popen[str] | None = None
        self.license_file = "Documentation/gpl-3.0.txt"
        self.about_file = "Documentation/about.txt"

        # Platform specific needs
        if platform.system() == "Windows":
            self.python_exe = "pyw"
        else:
            self.python_exe = "python3"

        if platform.system() == "Darwin":
            if not os.path.exists(f"{os.getcwd()}/lights_updater.py"):
                os.chdir(self.get_real_app_dir())

    def show_gui(self) -> None:
        """Creates the primary GUI for the user"""

        self.root = tkinter.Tk()
        self.root.title("Lights updater for CSL objects")

        # Center it on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = 1280
        height = 400
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.minsize(400, 300)

        # The menu
        self.menu = tkinter.Menu(self.root)
        self.root.config(menu=self.menu)
        self.file_menu = tkinter.Menu(self.menu, tearoff=False)

        self.file_menu.add_command(label="Exit", command=self.root.destroy)

        self.process_menu = tkinter.Menu(self.menu, tearoff=False)

        self.process_menu.add_command(
            label="Run standard conversion", command=self.start_conversion)

        self.process_menu.add_command(
            label="Run conversion with flashing beacons",
            command=self.start_conversion_with_flashing_beacons
        )

        self.process_menu.add_separator()

        self.process_menu.add_command(
            label="Run undo", command=self.undo_conversion)

        self.process_menu.add_separator()

        self.process_menu.add_command(
            label="Remove backup files! Be careful!",
            command=self.remove_backup_files,
            background="red",
            foreground="yellow"
        )

        self.CSL_menu = tkinter.Menu(self.menu, tearoff=False)

        self.CSL_menu.add_command(
            label="Select CSL directory",
            command=self.set_csl_directory
        )

        self.help_menu = tkinter.Menu(self.menu, tearoff=False)
        self.help_menu.add_command(
            label="Show version", command=self.show_version
        )
        self.help_menu.add_command(
            label="Show license", command=self.show_license
        )
        self.help_menu.add_command(
            label="About", command=self.show_about
        )

        self.menu.add_cascade(
            label="File",
            menu=self.file_menu,
            underline=0
        )

        self.menu.add_cascade(
            label="Converter",
            menu=self.process_menu,
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

        # In case of panic
        self.cancel_button = tkinter.Button(
            self.root, text="Cancel", command=self.cancel_process, state=tkinter.DISABLED)
        self.cancel_button.pack()

        # processing line
        self.process_frame = tkinter.Frame(self.root)
        self.process_frame.pack(anchor="nw")

        self.process_label = tkinter.Label(
            self.process_frame, text="Processing: ", padx=5, pady=5
        )
        self.process_label.pack(side=tkinter.LEFT)

        self.process_info_label = tkinter.Label(
            self.process_frame, text="No processing running!", fg="blue", padx=5, pady=5
        )
        self.process_info_label.pack(side=tkinter.LEFT)

        # csl line
        self.csl_frame = tkinter.Frame(self.root)
        self.csl_frame.pack(anchor="nw")

        self.dir_label = tkinter.Label(
            self.csl_frame, text="CSL directory: ", padx=5, pady=5
        )
        self.dir_label.pack(side=tkinter.LEFT)

        if self.config["csl_path"] == "":
            self.selected_dir_label = tkinter.Label(
                self.csl_frame, text="not selected!", fg="red", padx=5, pady=5)
        else:
            if os.path.exists(self.config["csl_path"]):
                self.selected_dir_label = tkinter.Label(
                    self.csl_frame, text=f"{self.config['csl_path']}", fg="green", padx=5, pady=5)
            else:
                self.selected_dir_label = tkinter.Label(
                    self.csl_frame, text=f"Path does not exist: {self.config['csl_path']}", fg="red", padx=5, pady=5)

        self.selected_dir_label.pack(side=tkinter.LEFT)

        # The window to the world
        self.output = ScrolledText(self.root)
        self.output.pack(padx=10, pady=10, expand=True,
                         fill=tkinter.BOTH, side=tkinter.LEFT)

        old_stdout = sys.stdout
        sys.stdout = StdOutRedirect(self.output)
        sys.stderr = StdOutRedirect(self.output)

        self.root.mainloop()
        sys.stdout = old_stdout

    def run_process(self, cli_params: str, task: str) -> None:
        """ Running the choosen process task in a thread.
            So prohibiting double tasks and allow canceling the running task.

        Args:
            cli_params (str): The command line parameters which are sent to lights_updater.py
            task (str): A name for the running task
        """

        # Let only one thread run at a time
        if hasattr(self, 'worker_thread') and self.worker_thread.is_alive():  # type: ignore
            tkinter.messagebox.showwarning(  # type: ignore
                "Process Running", "A task is already running. Please wait.")
            return

        self.output.delete(1.0, tkinter.END)
        self.process_info_label.config(text=f"{task}", fg="blue")
        self.cancel_requested = False
        self.cancel_button.config(state=tkinter.NORMAL)

        cmd: list[str] = [self.python_exe, "lights_updater.py", "--path",
                          self.config["csl_path"], "--from-gui"]

        if cli_params:
            cmd[-1:-1] = shlex.split(cli_params)

        def upater_task_thread() -> None:
            """Here the threading magic happens"""

            status_text = ""
            status_color = "green"
            try:
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )

                for line in iter(self.process.stdout.readline, ''):  # type: ignore
                    if self.cancel_requested:
                        break
                    self.output.after(0, self.output.insert, tkinter.END, line)
                    self.output.after(0, self.output.see, tkinter.END)
                self.process.stdout.close()  # type: ignore
                self.process.wait()

                if self.cancel_requested:
                    status_text = f"{task} cancelled by user."
                    status_color = "orange"
                elif self.process.returncode == 0:
                    status_text = f"{task} complete."
                    status_color = "green"
                else:
                    status_text = f"{task} failed (exit {self.process.returncode})"
                    status_color = "red"

            except FileNotFoundError as e:
                msg = f"Command not found: {e.filename}\n"
            except subprocess.SubprocessError as e:
                msg = f"Subprocess error: {str(e)}\n"
            except OSError as e:
                msg = f"System error: {e.strerror} (errno {e.errno})\n"
            except Exception as e:
                msg = f"Unexpected error ({type(e).__name__}): {str(e)}\n"
            else:
                return  # No exception, don't show error
            finally:
                self.process_info_label.config(
                    text=status_text, fg=status_color)
                self.cancel_button.config(state=tkinter.DISABLED)
                self.process = None

            # Show the error in GUI output
            if msg != "":
                self.output.after(0, self.output.insert, tkinter.END, msg)
                self.output.after(0, self.output.see, tkinter.END)
                self.output.after(0, self.process_info_label.config, {
                    'text': f"{task} failed.", 'fg': "red"})

        self.worker_thread = threading.Thread(
            target=upater_task_thread, daemon=True)
        self.worker_thread.start()

    def cancel_process(self) -> None:
        """ Stops the running task thread"""

        if hasattr(self, 'process') and self.process:
            self.cancel_requested = True
            self.process.terminate()
            self.output.insert(tkinter.END, "\nProcess cancelled by user.\n")
            self.output.see(tkinter.END)

    def start_conversion(self) -> None:
        """ Runs the normal conversion task with rotating beacons"""

        if self.config["csl_path"] == "":
            messagebox.showerror(  # type: ignore
                "Error", "No CSL directory selected")
            return
        self.process_info_label.config(
            text="Run 'normal' conversion", fg="green")
        cli_params = ""
        self.run_process(cli_params, "Standard conversion")

    def start_conversion_with_flashing_beacons(self) -> None:
        """" Runs the conversion task with flashing beacons"""

        if self.config["csl_path"] == "":
            messagebox.showerror(  # type: ignore
                "Error", "No CSL directory selected")
            return
        self.process_info_label.config(
            text="Run conversion with flashing beacons", fg="green")
        cli_params = "--flashing-beacons"
        self.run_process(cli_params, "Conversion with flashing beacons")

    def remove_backup_files(self) -> None:
        """ Runs the task to remove backup files permanently"""

        if self.config["csl_path"] == "":
            messagebox.showerror(  # type: ignore
                "Error", "No CSL directory selected")
            return
        self.process_info_label.config(
            text="Removing backups. Be careful!", fg="red1", font="bold")
        answer: bool = self.show_decision_box(
            "Warning!!", "You will delete all backups. Continue?")
        if answer:
            cli_params = "--remove-backups"
            self.run_process(cli_params, "Removing backups")
        else:
            self.process_info_label.config(
                text="No backups removed.", fg="green", font="TkDefaultFont")
            print("No backups removed.", flush=True)
            return

    def undo_conversion(self):
        """ Runs the recovery task to recover the original files from the backup files"""

        if self.config["csl_path"] == "":
            messagebox.showerror(  # type: ignore
                "Error", "No CSL directory selected")
            return
        self.process_info_label.config(
            text="Undoing prior conversions", fg="green")
        cli_params = "--undo"
        self.run_process(cli_params, "Recover to backuped files")

    def set_csl_directory(self) -> None:
        """ Sets the path to the CSL directory with the aircarft objects"""

        csl_directory: str = filedialog.askdirectory(
            parent=self.root,
            initialdir=self.config["csl_path"],
            title="Select CSL directory",
            mustexist=True
        )

        if csl_directory:
            self.config["csl_path"] = csl_directory
            self.selected_dir_label.config(text=csl_directory, fg="green")
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)

    def show_decision_box(self, title: str, message: str) -> bool:
        return messagebox.askyesno(title, message)  # type: ignore

    def show_version(self) -> None:
        self.process_info_label.config(text="Programm version", fg="green")
        cli_params = "--version"
        self.run_process(cli_params, "Getting version info")

    def get_real_app_dir(self) -> str:
        """Returns the directory where the executable lives on disk."""
        if hasattr(sys, '_MEIPASS'):
            # For --onefile: get path of the extracted executable
            return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(p=sys.executable))))
        else:
            # For --onedir or running normally
            return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def show_license(self) -> None:
        self.output.delete(1.0, tkinter.END)
        self.process_info_label.config(
            text="Showing program license", fg="green")
        with open(self.license_file, 'r') as f:
            license_text = f.read()
        self.output.insert("1.0", license_text)
        self.output.see("1.0")

    def show_about(self) -> None:
        self.output.delete(1.0, tkinter.END)
        self.process_info_label.config(text="Showing program info", fg="green")
        with open(self.about_file, 'r') as f:
            about_text = f.read()
        self.output.insert("1.0", about_text)
        self.output.see("1.0")


if __name__ == "__main__":
    # Get config from file or build a config file with basic settings.
    config: dict[str, Any] = {}
    config_file = "configs/config.json"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            if config["csl_path"] == "":
                config["csl_path"] = os.getcwd()
    else:
        config["csl_path"] = os.getcwd()
        config["interactive"] = True
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
    # Remove splash screen, if not on macOS.
    # MacOS prohibits splashscreens for pyinstaller.
    if platform.system() != "Darwin":
        try:
            import pyi_splash  # type: ignore
            pyi_splash.close()
        except ImportError:
            # pyi_splash is not installed or not needed, just ignore it!
            pass
    app = UpdaterGui(config, config_file)
    app.show_gui()
