from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, scrolledtext

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
        root_frame = tk.Frame(self.root, padx=16, pady=16)
        root_frame.pack(fill=tk.BOTH, expand=True)

        # ── Settings checkboxes ──────────────────────────────────────────────
        tk.Checkbutton(
            root_frame,
            text="Launch Chrome recovery on login",
            variable=self.autostart_var,
        ).pack(anchor="w")
        tk.Checkbutton(
            root_frame,
            text="Restore last session for each profile",
            variable=self.restore_var,
        ).pack(anchor="w", pady=(4, 12))

        # ── Profiles section ─────────────────────────────────────────────────
        tk.Label(root_frame, text="Profiles", font=("", 10, "bold")).pack(
            anchor="w", pady=(0, 4)
        )

        prof_frame = tk.Frame(root_frame)
        prof_frame.pack(fill=tk.X, pady=(0, 12))

        scrollbar = tk.Scrollbar(prof_frame, orient=tk.VERTICAL)
        self.profile_list = tk.Listbox(
            prof_frame,
            height=6,
            selectmode=tk.EXTENDED,
            yscrollcommand=scrollbar.set,
            exportselection=False,
        )
        scrollbar.config(command=self.profile_list.yview)
        self.profile_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self._refresh_profile_list()

        prof_btn_frame = tk.Frame(root_frame)
        prof_btn_frame.pack(fill=tk.X, pady=(0, 12))

        tk.Button(
            prof_btn_frame, text="Remove selected", command=self._remove_selected
        ).pack(side=tk.LEFT)
        tk.Button(
            prof_btn_frame, text="Remove all", command=self._remove_all
        ).pack(side=tk.LEFT, padx=(4, 0))
        tk.Button(
            prof_btn_frame, text="Restore selected", command=self._restore_selected
        ).pack(side=tk.LEFT, padx=(4, 0))
        tk.Button(
            prof_btn_frame, text="Restore all", command=self._restore_all
        ).pack(side=tk.LEFT, padx=(4, 0))

        # ── Action buttons ────────────────────────────────────────────────────
        btn_frame = tk.Frame(root_frame)
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text="Save", command=self._save).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Recover Now", command=self._recover_now).pack(
            side=tk.LEFT, padx=(8, 0)
        )
        tk.Button(btn_frame, text="Snapshot", command=self._snapshot).pack(
            side=tk.LEFT, padx=(8, 0)
        )
        tk.Button(btn_frame, text="Close", command=self.root.destroy).pack(
            side=tk.RIGHT
        )

    # ── Profile list helpers ─────────────────────────────────────────────────

    def _refresh_profile_list(self) -> None:
        from chromeopen.profiles import _all_profiles, ignored_profiles

        self.profile_list.delete(0, tk.END)
        ignored = set(ignored_profiles())
        for p in _all_profiles():
            label = f"[ignored] {p}" if p in ignored else p
            self.profile_list.insert(tk.END, label)

    def _selected_profile_names(self) -> list[str]:
        items = [self.profile_list.get(i) for i in self.profile_list.curselection()]
        return [i.replace("[ignored] ", "") for i in items]

    def _remove_selected(self) -> None:
        from chromeopen.profiles import remove_profile

        names = self._selected_profile_names()
        if not names:
            messagebox.showinfo("Remove profiles", "Select at least one profile.")
            return
        for name in names:
            remove_profile(name)
        self._refresh_profile_list()

    def _remove_all(self) -> None:
        from chromeopen.profiles import remove_all_profiles

        removed = remove_all_profiles()
        self._refresh_profile_list()
        if removed:
            messagebox.showinfo(
                "Remove all profiles",
                f"Ignored {len(removed)} profile(s):\n" + "\n".join(removed),
            )
        else:
            messagebox.showinfo("Remove all profiles", "No active profiles to ignore.")

    def _restore_selected(self) -> None:
        from chromeopen.profiles import restore_profile

        names = self._selected_profile_names()
        if not names:
            messagebox.showinfo("Restore profiles", "Select at least one profile.")
            return
        for name in names:
            restore_profile(name)
        self._refresh_profile_list()

    def _restore_all(self) -> None:
        from chromeopen.profiles import restore_all_profiles

        restore_all_profiles()
        self._refresh_profile_list()
        messagebox.showinfo("Restore all profiles", "All profiles restored.")

    # ── Save / recover / snapshot ─────────────────────────────────────────────

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
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Autostart Error", str(exc))
            return
        messagebox.showinfo("Saved", "Settings saved.")

    def _recover_now(self) -> None:
        from chromeopen.main import recover_profiles

        recover_profiles(settings_store.load_settings())
        messagebox.showinfo("Recovery", "Recovery started.")

    def _snapshot(self) -> None:
        from chromeopen.snapshot import take_snapshot, load_snapshot
        import json

        path = take_snapshot()
        data = load_snapshot(path)
        total = sum(len(v) for v in data.values())

        win = tk.Toplevel(self.root)
        win.title("Snapshot")
        win.resizable(True, True)

        header = f"Snapshot saved: {path}\n{len(data)} profile(s), {total} tab(s)\n"
        tk.Label(win, text=header, justify=tk.LEFT, padx=8, pady=4).pack(anchor="w")

        text = scrolledtext.ScrolledText(win, width=90, height=24, wrap=tk.NONE)
        text.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        text.insert(tk.END, json.dumps(data, indent=2, ensure_ascii=False))
        text.config(state=tk.DISABLED)

        tk.Button(win, text="Close", command=win.destroy).pack(pady=(0, 8))

    def run(self) -> None:
        self.root.mainloop()


def open_settings_ui() -> None:
    SettingsUI().run()
