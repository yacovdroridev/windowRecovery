from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from chromeopen import settings as settings_store
from chromeopen.autostart import disable_autostart, enable_autostart


class SettingsUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("ChromeOpen Settings")
        self.root.resizable(False, False)

        current = settings_store.load_settings()
        self.autostart_var = tk.BooleanVar(value=bool(current.get("autostart")))
        self.restore_var = tk.BooleanVar(value=bool(current.get("restore_last_session")))

        self._build()

    def _build(self) -> None:
        frame = tk.Frame(self.root, padx=16, pady=16)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Checkbutton(
            frame,
            text="Launch Chrome recovery on login",
            variable=self.autostart_var,
        ).pack(anchor="w")
        tk.Checkbutton(
            frame,
            text="Restore last session for each profile",
            variable=self.restore_var,
        ).pack(anchor="w", pady=(8, 12))

        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text="Save", command=self._save).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Recover Now", command=self._recover_now).pack(
            side=tk.LEFT, padx=(8, 0)
        )
        tk.Button(btn_frame, text="Close", command=self.root.destroy).pack(
            side=tk.RIGHT
        )

    def _save(self) -> None:
        settings = {
            "autostart": bool(self.autostart_var.get()),
            "restore_last_session": bool(self.restore_var.get()),
        }
        settings_store.save_settings(settings)
        try:
            if settings["autostart"]:
                enable_autostart()
            else:
                disable_autostart()
        except Exception as exc:  # noqa: BLE001 - surface error in UI
            messagebox.showerror("Autostart Error", str(exc))
            return
        messagebox.showinfo("Saved", "Settings saved.")

    def _recover_now(self) -> None:
        from chromeopen.main import recover_profiles

        recover_profiles(settings_store.load_settings())
        messagebox.showinfo("Recovery", "Recovery started.")

    def run(self) -> None:
        self.root.mainloop()


def open_settings_ui() -> None:
    SettingsUI().run()
