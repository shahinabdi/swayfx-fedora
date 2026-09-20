"""Full-screen curses interface for Fedora SwayFX.

Uses only the standard library so the installer keeps its zero-dependency
policy while still working over SSH and in a plain terminal emulator.
"""

from __future__ import annotations

import curses

from .config_manager import ConfigManager
from .doctor import Doctor
from .installer import Installer
from .models import ConfigAction, InstallMode, PackageSpec

TITLE = "Fedora SwayFX"
SUBTITLE = "Modern Wayland desktop setup"

CATEGORY_LABELS = {
    "Core SwayFX": "Core",
    "Terminal": "Terminal",
    "Desktop utilities": "Utilities",
    "Applications": "Applications",
}

MIN_HEIGHT = 18
MIN_WIDTH = 54

# color pair ids
C_TEXT = 1
C_ACCENT = 2
C_SELECTED = 3
C_SUCCESS = 4
C_ERROR = 5
C_WARN = 6
C_DIM = 7


class Cancelled(Exception):
    """Raised internally to unwind a screen back to the main menu."""


def run(installer: Installer) -> int:
    try:
        return curses.wrapper(lambda stdscr: App(stdscr, installer).run())
    except KeyboardInterrupt:
        print("\nCancelled.")
        return 130


def _clip(text: str, width: int) -> str:
    return text if len(text) <= width else text[: max(0, width)]


def _addstr(win, y: int, x: int, text: str, attr: int = 0) -> None:
    height, width = win.getmaxyx()
    if y < 0 or y >= height or x < 0 or x >= width:
        return
    try:
        win.addstr(y, x, _clip(text, width - x - 1), attr)
    except curses.error:
        pass


def _box(win, title: str | None = None, color: int = 0) -> None:
    win.erase()
    win.attron(color)
    win.box()
    if title:
        win.addstr(0, 2, f" {title} ", color | curses.A_BOLD)
    win.attroff(color)


class App:
    def __init__(self, stdscr, installer: Installer) -> None:
        self.stdscr = stdscr
        self.installer = installer
        curses.curs_set(0)
        stdscr.keypad(True)
        self._init_colors()

    def _init_colors(self) -> None:
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(C_TEXT, curses.COLOR_WHITE, -1)
        curses.init_pair(C_ACCENT, curses.COLOR_BLUE, -1)
        curses.init_pair(C_SELECTED, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(C_SUCCESS, curses.COLOR_GREEN, -1)
        curses.init_pair(C_ERROR, curses.COLOR_RED, -1)
        curses.init_pair(C_WARN, curses.COLOR_YELLOW, -1)
        curses.init_pair(C_DIM, curses.COLOR_WHITE, -1)

    def color(self, pair: int, *, bold: bool = False, dim: bool = False) -> int:
        attr = curses.color_pair(pair)
        if bold:
            attr |= curses.A_BOLD
        if dim:
            attr |= curses.A_DIM
        return attr

    # -- top level loop -----------------------------------------------------

    def run(self) -> int:
        while True:
            if not self._check_size():
                return 0
            choice = self.main_menu()
            if choice in (None, "exit"):
                return 0
            try:
                if choice == "full":
                    self.run_mode(InstallMode.FULL, "Full Setup")
                elif choice == "configure":
                    self.configure_screen()
                elif choice == "apps":
                    self.run_mode(InstallMode.APPS, "Applications")
                elif choice == "custom":
                    self.run_mode(InstallMode.CUSTOM, "Custom Installation")
                elif choice == "doctor":
                    self.doctor_screen()
                elif choice == "uninstall":
                    self.uninstall_screen()
            except Cancelled:
                continue

    def _check_size(self) -> bool:
        height, width = self.stdscr.getmaxyx()
        if height >= MIN_HEIGHT and width >= MIN_WIDTH:
            return True
        self.stdscr.erase()
        _addstr(self.stdscr, 0, 0, "Terminal too small - resize and press any key (q to quit).", self.color(C_WARN))
        self.stdscr.refresh()
        key = self.stdscr.getch()
        return key not in (ord("q"), 27)

    # -- main menu ------------------------------------------------------

    def main_menu(self) -> str | None:
        items = [
            ("full", "Full Setup"),
            ("configure", "Configure Desktop"),
            ("apps", "Applications"),
            ("custom", "Custom Installation"),
            ("doctor", "Doctor"),
            ("uninstall", "Uninstall / Restore"),
            ("exit", "Exit"),
        ]
        detection = self.installer.detector.detect(["swayfx"])
        index = 0
        while True:
            self._render_main_menu(items, index, detection)
            key = self.stdscr.getch()
            if key in (curses.KEY_UP, ord("k")):
                index = (index - 1) % len(items)
            elif key in (curses.KEY_DOWN, ord("j")):
                index = (index + 1) % len(items)
            elif key in (curses.KEY_ENTER, 10, 13):
                return items[index][0]
            elif key in (ord("q"), 27):
                return "exit"
            elif key == 3:  # Ctrl+C
                raise KeyboardInterrupt

    def _render_main_menu(self, items, index, detection) -> None:
        height, width = self.stdscr.getmaxyx()
        self.stdscr.erase()
        accent = self.color(C_ACCENT, bold=True)
        text = self.color(C_TEXT)
        dim = self.color(C_DIM, dim=True)
        _box(self.stdscr, color=accent)
        _addstr(self.stdscr, 1, 3, TITLE, accent)
        _addstr(self.stdscr, 2, 3, SUBTITLE, dim)
        _addstr(self.stdscr, 3, 1, "-" * (width - 2), accent)

        row = 5
        _addstr(self.stdscr, row, 3, "System", accent)
        row += 1
        _addstr(self.stdscr, row, 5, f"Fedora {detection.fedora_version} {detection.architecture}", text)
        row += 1
        _addstr(self.stdscr, row, 5, "KDE Plasma", text)
        _addstr(self.stdscr, row, 20, "\u2713" if detection.kde else "\u2717", self.color(C_SUCCESS if detection.kde else C_WARN))
        row += 1
        _addstr(self.stdscr, row, 5, "Wayland", text)
        _addstr(self.stdscr, row, 20, "\u2713" if detection.wayland else "\u2717", self.color(C_SUCCESS if detection.wayland else C_WARN))
        row += 1
        swayfx_installed = detection.packages.get("swayfx", False)
        _addstr(self.stdscr, row, 5, "SwayFX", text)
        _addstr(self.stdscr, row, 20, "\u2713" if swayfx_installed else "\u2717", self.color(C_SUCCESS if swayfx_installed else C_ERROR))

        row += 2
        _addstr(self.stdscr, row, 3, "What would you like to do?", text)
        row += 2
        for offset, (_, label) in enumerate(items):
            selected = offset == index
            attr = self.color(C_SELECTED, bold=True) if selected else text
            prefix = "> " if selected else "  "
            _addstr(self.stdscr, row + offset, 5, f"{prefix}{label}", attr)

        footer = "Up/Down: navigate  Enter: select  q: exit"
        _addstr(self.stdscr, height - 2, 3, footer, dim)
        self.stdscr.refresh()

    # -- generic helpers --------------------------------------------------

    def message_screen(self, title: str, lines: list[tuple[str, int]], footer: str = "Press any key to continue") -> None:
        height, width = self.stdscr.getmaxyx()
        self.stdscr.erase()
        accent = self.color(C_ACCENT, bold=True)
        _box(self.stdscr, title=title, color=accent)
        for offset, (line, attr) in enumerate(lines):
            if 2 + offset >= height - 2:
                break
            _addstr(self.stdscr, 2 + offset, 3, line, attr)
        _addstr(self.stdscr, height - 2, 3, footer, self.color(C_DIM, dim=True))
        self.stdscr.refresh()
        self.stdscr.getch()

    def confirm_dialog(self, title: str, lines: list[str], default: bool = True) -> bool:
        height, width = self.stdscr.getmaxyx()
        box_h = min(height - 4, len(lines) + 6)
        box_w = min(width - 4, max(len(title) + 6, max((len(line) for line in lines), default=0) + 6, 40))
        win = curses.newwin(box_h, box_w, (height - box_h) // 2, (width - box_w) // 2)
        choice = 0 if default else 1
        options = ["Yes", "No"]
        text = self.color(C_TEXT)
        while True:
            _box(win, title=title, color=self.color(C_ACCENT, bold=True))
            for offset, line in enumerate(lines):
                if 1 + offset >= box_h - 3:
                    break
                _addstr(win, 1 + offset, 2, line, text)
            button_row = box_h - 2
            x = 2
            for i, label in enumerate(options):
                attr = self.color(C_SELECTED, bold=True) if i == choice else text
                _addstr(win, button_row, x, f"[ {label} ]", attr)
                x += len(label) + 5
            win.refresh()
            key = self.stdscr.getch()
            if key in (curses.KEY_LEFT, curses.KEY_RIGHT, ord("\t")):
                choice = 1 - choice
            elif key in (curses.KEY_ENTER, 10, 13):
                return choice == 0
            elif key in (ord("y"), ord("Y")):
                return True
            elif key in (ord("n"), ord("N"), 27):
                return False
            elif key == 3:
                raise KeyboardInterrupt

    def list_dialog(self, title: str, options: list[str]) -> int | None:
        height, width = self.stdscr.getmaxyx()
        box_h = min(height - 4, len(options) + 4)
        box_w = min(width - 4, max((len(option) for option in options), default=0) + 8)
        win = curses.newwin(box_h, box_w, (height - box_h) // 2, (width - box_w) // 2)
        index = 0
        text = self.color(C_TEXT)
        while True:
            _box(win, title=title, color=self.color(C_ACCENT, bold=True))
            for offset, option in enumerate(options):
                attr = self.color(C_SELECTED, bold=True) if offset == index else text
                prefix = "> " if offset == index else "  "
                _addstr(win, 1 + offset, 2, f"{prefix}{option}", attr)
            win.refresh()
            key = self.stdscr.getch()
            if key in (curses.KEY_UP, ord("k")):
                index = (index - 1) % len(options)
            elif key in (curses.KEY_DOWN, ord("j")):
                index = (index + 1) % len(options)
            elif key in (curses.KEY_ENTER, 10, 13):
                return index
            elif key == 27:
                return None
            elif key == 3:
                raise KeyboardInterrupt

    # -- custom installation / checkbox screen ----------------------------

    def run_mode(self, mode: InstallMode, title: str) -> None:
        catalog = self.installer.package_catalog()
        if mode == InstallMode.APPS:
            catalog = [item for item in catalog if item.category == "Applications"]
        elif mode == InstallMode.FULL:
            catalog = [item for item in catalog if item.category != "Applications"]
        selected = {item.name: item.default for item in catalog}
        packages = self.checkbox_screen(title, catalog, selected)
        if packages is None:
            return
        self.install_flow(packages)

    def checkbox_screen(self, title: str, catalog: list[PackageSpec], selected: dict[str, bool]) -> list[PackageSpec] | None:
        filter_text = ""
        index = 0
        top = 0
        searching = False
        while True:
            rows = self._build_rows(catalog, filter_text)
            if not rows:
                index = 0
            else:
                index = max(0, min(index, len(rows) - 1))
            height, width = self.stdscr.getmaxyx()
            visible_height = height - 12
            if index < top:
                top = index
            elif index >= top + visible_height:
                top = index - visible_height + 1
            self._render_checkbox(title, rows, index, top, visible_height, selected, filter_text, searching)
            key = self.stdscr.getch()
            if searching:
                if key in (27,):
                    searching = False
                elif key in (curses.KEY_ENTER, 10, 13):
                    searching = False
                elif key in (curses.KEY_BACKSPACE, 127, 8):
                    filter_text = filter_text[:-1]
                elif 32 <= key < 127:
                    filter_text += chr(key)
                continue
            if key in (curses.KEY_UP, ord("k")):
                index = max(0, index - 1)
            elif key in (curses.KEY_DOWN, ord("j")):
                index = min(len(rows) - 1, index + 1) if rows else 0
            elif key == ord(" ") and rows:
                self._toggle_row(rows[index], selected)
            elif key in (ord("a"), ord("A")):
                for item in catalog:
                    selected[item.name] = True
            elif key in (ord("n"), ord("N")):
                for item in catalog:
                    selected[item.name] = False
            elif key in (ord("d"), ord("D")):
                for item in catalog:
                    selected[item.name] = item.default
            elif key in (ord("/"), ord("f")):
                searching = True
            elif key in (curses.KEY_ENTER, 10, 13):
                return [item for item in catalog if selected[item.name]]
            elif key in (ord("q"), 27):
                return None
            elif key == 3:
                raise KeyboardInterrupt

    def _build_rows(self, catalog: list[PackageSpec], filter_text: str):
        rows: list[tuple] = []
        needle = filter_text.lower()
        categories: list[str] = []
        for item in catalog:
            if item.category not in categories:
                categories.append(item.category)
        for category in categories:
            items = [item for item in catalog if item.category == category]
            if needle:
                items = [item for item in items if needle in item.label.lower() or needle in item.name.lower()]
                if not items:
                    continue
            rows.append(("header", category, [item.name for item in items]))
            rows.extend(("item", item) for item in items)
        return rows

    def _toggle_row(self, row: tuple, selected: dict[str, bool]) -> None:
        if row[0] == "header":
            names = row[2]
            state = not all(selected[name] for name in names)
            for name in names:
                selected[name] = state
        else:
            item: PackageSpec = row[1]
            selected[item.name] = not selected[item.name]

    def _render_checkbox(self, title, rows, index, top, visible_height, selected, filter_text, searching) -> None:
        height, width = self.stdscr.getmaxyx()
        self.stdscr.erase()
        accent = self.color(C_ACCENT, bold=True)
        text = self.color(C_TEXT)
        dim = self.color(C_DIM, dim=True)
        _box(self.stdscr, title=title, color=accent)

        row_y = 2
        visible = rows[top : top + visible_height]
        for offset, row in enumerate(visible):
            y = row_y + offset
            actual_index = top + offset
            is_current = actual_index == index
            if row[0] == "header":
                label = CATEGORY_LABELS.get(row[1], row[1])
                attr = self.color(C_SELECTED, bold=True) if is_current else self.color(C_ACCENT, bold=True)
                _addstr(self.stdscr, y, 3, label, attr)
            else:
                item: PackageSpec = row[1]
                box = "\u2612" if selected[item.name] else "\u2610"
                attr = self.color(C_SELECTED, bold=True) if is_current else text
                _addstr(self.stdscr, y, 5, f"{box} {item.label}", attr)

        footer_y = height - 5
        _addstr(self.stdscr, footer_y, 3, "Space: select  Up/Down: navigate  /: search", dim)
        _addstr(self.stdscr, footer_y + 1, 3, "A: all  N: none  D: defaults", dim)
        if searching:
            _addstr(self.stdscr, footer_y + 2, 3, f"Search: {filter_text}", self.color(C_ACCENT, bold=True))
        elif filter_text:
            _addstr(self.stdscr, footer_y + 2, 3, f"Filter: {filter_text} (press / to edit)", dim)
        _addstr(self.stdscr, height - 2, 3, "[ Install ]", self.color(C_SUCCESS, bold=True))
        _addstr(self.stdscr, height - 2, 18, "[ Cancel ]", dim)
        _addstr(self.stdscr, height - 2, 32, "Enter: install  Esc: cancel", dim)
        self.stdscr.refresh()

    # -- install progress ---------------------------------------------------

    def install_flow(self, packages: list[PackageSpec]) -> None:
        plan = self.installer.packages.plan(packages)
        if not plan.to_install:
            self.message_screen("Nothing to do", [("All selected packages are already installed.", self.color(C_TEXT))])
            return
        lines = [item.label for item in plan.to_install]
        if plan.unavailable:
            lines.append("")
            lines.append("Unavailable (skipped): " + ", ".join(item.label for item in plan.unavailable))
        if not self.confirm_dialog("Confirm installation", [f"Install {len(plan.to_install)} package(s)?"] + lines[:8]):
            return
        self._progress_screen(list(plan.to_install))

    def _progress_screen(self, items: list[PackageSpec]) -> None:
        status: dict[str, str] = {item.name: "pending" for item in items}
        total = len(items)
        done_count = 0

        def on_progress(item: PackageSpec, event: str) -> None:
            nonlocal done_count
            status[item.name] = event
            if event in ("done", "failed"):
                done_count += 1
            self._render_progress(items, status, done_count, total)

        self._render_progress(items, status, done_count, total)
        success = self.installer.packages.install(items, verbose=self.installer.verbose, on_progress=on_progress)
        summary = "Installation complete" if success else "Installation finished with errors"
        lines = []
        for item in items:
            state = status[item.name]
            color = self.color(C_SUCCESS) if state == "done" else self.color(C_ERROR) if state == "failed" else self.color(C_TEXT)
            lines.append((f"{item.label}: {state}", color))
        self.message_screen(summary, lines, footer="Press any key to continue")

    def _render_progress(self, items: list[PackageSpec], status: dict[str, str], done_count: int, total: int) -> None:
        height, width = self.stdscr.getmaxyx()
        self.stdscr.erase()
        accent = self.color(C_ACCENT, bold=True)
        text = self.color(C_TEXT)
        _box(self.stdscr, title="Installing", color=accent)
        current = next((item.label for item in items if status[item.name] == "start"), "Preparing...")
        _addstr(self.stdscr, 2, 3, f"Installing {current}", accent)

        bar_width = max(10, width - 10)
        percent = int((done_count / total) * 100) if total else 100
        filled = int(bar_width * percent / 100)
        bar = "\u2588" * filled + "\u2591" * (bar_width - filled)
        _addstr(self.stdscr, 3, 3, f"[{bar}] {percent:3d}%", accent)

        row = 5
        for item in items:
            if row >= height - 2:
                break
            state = status[item.name]
            if state == "done":
                icon, color = "\u2713", self.color(C_SUCCESS, bold=True)
            elif state == "failed":
                icon, color = "\u2717", self.color(C_ERROR, bold=True)
            elif state == "start":
                icon, color = "\u2192", self.color(C_ACCENT, bold=True)
            else:
                icon, color = "\u25cb", self.color(C_DIM, dim=True)
            _addstr(self.stdscr, row, 3, f"{icon} {item.label}", color)
            row += 1
        self.stdscr.refresh()

    # -- configure / doctor / uninstall screens ------------------------------

    def configure_screen(self) -> None:
        existing = any(self.installer.config.home.joinpath(".config", name).exists() for name in ConfigManager.CONFIG_MAP)
        action = ConfigAction.BACKUP_REPLACE
        if existing:
            options = ["Backup and replace", "Skip existing", "Keep existing", "Cancel"]
            choice = self.list_dialog("Existing configuration found", options)
            if choice is None or choice == 3:
                return
            action = [ConfigAction.BACKUP_REPLACE, ConfigAction.SKIP, ConfigAction.KEEP][choice]
        if not self.confirm_dialog("Confirm", ["Install configuration files now?"]):
            return
        try:
            changed = self.installer.config.install(action)
        except RuntimeError as error:
            self.message_screen("Configuration cancelled", [(str(error), self.color(C_ERROR))])
            return
        lines = [(str(path), self.color(C_TEXT)) for path in changed] or [("Nothing changed.", self.color(C_TEXT))]
        self.message_screen("Configuration updated", lines)

    def doctor_screen(self) -> None:
        report = Doctor(self.installer.detector).report()
        lines = []
        for name, status, detail in report:
            color = self.color(C_SUCCESS) if status == "PASS" else self.color(C_WARN) if status == "WARN" else self.color(C_ERROR)
            lines.append((f"{status:5} {name:18} {detail}", color))
        self.message_screen("Doctor", lines)

    def uninstall_screen(self) -> None:
        if not self.confirm_dialog("Uninstall", ["Remove project-managed configuration and restore backups?"], default=False):
            return
        removed = self.installer.config.uninstall()
        lines = [(str(path), self.color(C_TEXT)) for path in removed] or [("Nothing to remove.", self.color(C_TEXT))]
        self.message_screen("Uninstall complete", lines)
