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
        self.widget.insert(tkinter.END, text)
        # self.widget.see(tkinter.END)

    def flush(self):
        pass


class UpdaterGui:
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
        self.root.minsize(400, 300)

        self.root.title("Lights updater for CSL objects")
        self.selected_dir_label = tkinter.Label(
            self.root, text="No CSL directory selected!", fg="red", padx=5, pady=5)
        self.selected_dir_label.pack()

        self.output = ScrolledText(self.root)
        self.output.pack(padx=10, pady=10, expand=True,
                         fill=tkinter.BOTH, side=tkinter.LEFT)

        old_stdout = sys.stdout
        sys.stdout = StdOutRedirect(self.output)

        self.menu = tkinter.Menu(self.root)
        self.root.config(menu=self.menu)

        self.file_menu = tkinter.Menu(self.menu, tearoff=False)

        self.file_menu.add_command(
            label="Run conversion", command=self.run_conversion)
        self.file_menu.add_command(
            label="Run conversion with flashing beacons",
            command=self.run_flashing_conversion
        )
        self.file_menu.add_command(
            label="Remove backup files", command=self.run_removing_backups
        )
        self.file_menu.add_command(
            label="Run undo", command=self.run_undo)
        self.file_menu.add_command(label="Exit", command=self.root.destroy)

        self.config_menu = tkinter.Menu(self.menu, tearoff=False)

        self.config_menu.add_command(
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
            label="Config",
            menu=self.config_menu,
            underline=0
        )

        self.menu.add_cascade(
            label="Help",
            menu=self.help_menu,
            underline=0
        )

        self.root.mainloop()
        sys.stdout = old_stdout

    def run_undo(self) -> None:
        threading.Thread(target=self.undo_conversion).start()

    def run_conversion(self) -> None:
        threading.Thread(target=self.start_conversion).start()

    def run_flashing_conversion(self) -> None:
        threading.Thread(
            target=self.startconversion_with_flashing_beacons).start()

    def run_removing_backups(self) -> None:
        threading.Thread(target=self.remove_backup_files).start()

    def run_process(self, cli_params: str) -> None:
        self.output.delete(1.0, tkinter.END)
        process: subprocess.Popen[str] | None = subprocess.Popen(
            f"python lights_updater.py {cli_params}".split(),
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0
        )
        while True:
            if process.poll() is not None:
                break
            msg: str = process.stdout.readline().strip()  # type: ignore
            if (msg):
                print(msg)
            else:
                break

    def undo_conversion(self):
        if "csl_path" in self.config:
            self.output.delete(1.0, tkinter.END)
            cli_params = f"--path {self.config['csl_path']} --undo --from_gui"
            self.run_process(cli_params)
        else:
            messagebox.showerror(  # type: ignore
                "Error", "No directory selected")

    def start_conversion(self) -> None:
        if "csl_path" in self.config:
            self.output.delete(1.0, tkinter.END)
            print("Run conversion")
            cli_params = f"--path {self.config['csl_path']} --from_gui"
            self.run_process(cli_params)
        else:
            messagebox.showerror(  # type: ignore
                "Error", "No directory selected")

    def startconversion_with_flashing_beacons(self) -> None:
        if "csl_path" in self.config:
            self.output.delete(1.0, tkinter.END)
            cli_params = f"--path {self.config['csl_path']} --flashing_beacons --from_gui"
            self.run_process(cli_params)
        else:
            messagebox.showerror(  # type: ignore
                "Error", "No directory selected")

    def remove_backup_files(self) -> None:
        if "csl_path" in self.config:
            self.output.delete(1.0, tkinter.END)
            answer = self.show_warning(
                "Warning", "You will delete all backups. Continue?")
            if answer:
                cli_params = f"--path {self.config['csl_path']} --remove-backups  --from_gui"
                self.run_process(cli_params)
            else:
                print("No backusp removed.")
                return
        else:
            messagebox.showerror(  # type: ignore
                "Error", "No directory selected")

    def show_version(self) -> None:
        self.output.delete(1.0, tkinter.END)
        process: subprocess.Popen[str] | None = subprocess.Popen(
            "python lights_updater.py --version".split(
            ),
            text=True, stdout=subprocess.PIPE, bufsize=1
        )
        while True:
            if process.poll() is not None:
                break
            msg: str = process.stdout.readline().strip()  # type: ignore
            if (msg):
                print(msg)
            else:
                break

    def set_csl_directory(self) -> None:
        csl_directory = filedialog.askdirectory(initialdir=".")

        if csl_directory:
            self.config["csl_path"] = csl_directory
            self.selected_dir_label.config(text=csl_directory, fg="green")

    def show_warning(self, title: str, message: str) -> bool:
        return messagebox.askyesno(title, message)  # type: ignore


if __name__ == "__main__":
    app = UpdaterGui()
    app.show_gui()
