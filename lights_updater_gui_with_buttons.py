#!/usr/bin/env python3
import tkinter
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

import sys
import subprocess
import threading
import shlex


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
        self.process: subprocess.Popen[str] | None = None

    def show_gui(self) -> None:
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
            label="Set CSL path",
            menu=self.CSL_menu,
            underline=0
        )

        self.menu.add_cascade(
            label="Help",
            menu=self.help_menu,
            underline=0
        )

        # The buttons
        self.button_frame = tkinter.Frame(self.root)
        self.button_frame.pack(anchor="nw")

        self.normal_conversion_button = tkinter.Button(
            self.button_frame,
            text="Normal conversion",
            command=self.start_conversion,
            width=20,
            bg="white")
        self.normal_conversion_button.pack(side=tkinter.LEFT, padx=5, pady=5)

        self.flashing_conversion_button = tkinter.Button(
            self.button_frame,
            text="Flashing conversion",
            command=self.start_conversion_with_flashing_beacons,
            width=20,
            bg="white")
        self.flashing_conversion_button.pack(side=tkinter.LEFT, padx=5, pady=5)

        self.undo_button = tkinter.Button(
            self.button_frame,
            text="Undo conversion",
            command=self.undo_conversion,
            width=20,
            bg="white")
        self.undo_button.pack(side=tkinter.LEFT, padx=5, pady=5)

        self.remove_backups_button = tkinter.Button(
            self.button_frame,
            text="Remove backup files",
            command=self.undo_conversion,
            width=20,
            bg="red")
        self.remove_backups_button.pack(side=tkinter.LEFT, padx=5, pady=5)

        # In case of PANIC!!
        self.cancel_button = tkinter.Button(
            self.root,
            text="Cancel",
            command=self.cancel_process,
            state=tkinter.DISABLED,
            width=40,
            bg="red",
            fg="white")
        self.cancel_button.pack(side=tkinter.BOTTOM, padx=5, pady=5)

        # The processing frame
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

        # The CSL frame
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
            self.selected_dir_label = tkinter.Label(
                self.csl_frame, text=f"{self.config['csl_path']}", fg="red", padx=5, pady=5)

        self.selected_dir_label.pack(side=tkinter.LEFT)

        # The window to the world... output, ouput baby!
        self.output = ScrolledText(self.root)
        self.output.pack(padx=10, pady=10, expand=True,
                         fill=tkinter.BOTH, side=tkinter.LEFT)

        old_stdout = sys.stdout
        sys.stdout = StdOutRedirect(self.output)
        sys.stderr = StdOutRedirect(self.output)

        self.root.mainloop()
        sys.stdout = old_stdout

    def run_process(self, cli_params: str, task: str) -> None:

        # Let only one thread run at a time
        if hasattr(self, 'worker_thread') and self.worker_thread.is_alive():  # type: ignore
            tkinter.messagebox.showwarning(  # type: ignore
                "Process Running", "A task is already running. Please wait.")
            return

        self.output.delete(1.0, tkinter.END)
        self.process_info_label.config(text=f"{task}", fg="blue")
        self.cancel_requested = False
        self.cancel_button.config(state=tkinter.NORMAL)

        cmd: list[str] = ["python3", "lights_updater.py", "--path",
                          self.config["csl_path"], "--from-gui"]
        if cli_params:
            cmd[-1:-1] = shlex.split(cli_params)

        def reader_thread() -> None:
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
                self.output.after(0, self.process_info_label.config, {
                    'text': status_text, 'fg': status_color})
                self.output.after(0, self.cancel_button.config, {
                    'state': tkinter.DISABLED})
                self.process = None

            # Show the error in GUI output
            if msg != "":
                self.output.after(0, self.output.insert, tkinter.END, msg)
                self.output.after(0, self.output.see, tkinter.END)
                self.output.after(0, self.process_info_label.config, {
                    'text': f"{task} failed.", 'fg': "red"})

        self.worker_thread = threading.Thread(
            target=reader_thread, daemon=True)
        self.worker_thread.start()

    def cancel_process(self) -> None:
        if hasattr(self, 'process') and self.process:
            self.cancel_requested = True
            self.process.terminate()
            self.output.insert(tkinter.END, "\nProcess cancelled by user.\n")
            self.output.see(tkinter.END)

    def start_conversion(self) -> None:
        if self.config["csl_path"] == "":
            messagebox.showerror(  # type: ignore
                "Error", "No CSL directory selected")
            return
        self.process_info_label.config(
            text="Run 'normal' conversion", fg="green")
        cli_params = ""
        self.run_process(cli_params, "Standard conversion")

    def start_conversion_with_flashing_beacons(self) -> None:
        if self.config["csl_path"] == "":
            messagebox.showerror(  # type: ignore
                "Error", "No directory selected")
            return
        self.process_info_label.config(
            text="Run conversion with flashing beacons", fg="green")
        cli_params = "--flashing-beacons"
        self.run_process(cli_params, "Conversion with flashing beacons")

    def remove_backup_files(self) -> None:
        if self.config["csl_path"] == "":
            messagebox.showerror(  # type: ignore
                "Error", "No CSL directory selected")
            return
        self.process_info_label.config(
            text="Removing backups. Be careful!", fg="red1", font="bold")
        answer: bool = self.show_delete_backups_warning(
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
        if self.config["csl_path"] == "":
            messagebox.showerror(  # type: ignore
                "Error", "No directory selected")
            return
        self.process_info_label.config(
            text="Undoing prior conversions", fg="green")
        cli_params = "--undo"
        self.run_process(cli_params, "Recover to backuped files")

    def show_version(self) -> None:
        self.process_info_label.config(text="Programm version", fg="green")
        cli_params = "--version"
        self.run_process(cli_params, "Getting version info")

    def set_csl_directory(self) -> None:
        csl_directory: str = filedialog.askdirectory(
            parent=self.root,
            initialdir=self.config["csl_path"],
            title="Select CSL directory",
            mustexist=True
        )

        if csl_directory:
            self.config["csl_path"] = csl_directory
            self.selected_dir_label.config(text=csl_directory, fg="green")

    def show_delete_backups_warning(self, title: str, message: str) -> bool:
        return messagebox.askyesno(title, message)  # type: ignore


if __name__ == "__main__":
    app = UpdaterGui()
    app.show_gui()
