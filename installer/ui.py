from __future__ import annotations

from collections.abc import Sequence

from .models import ConfigAction, InstallMode, PackageSpec


def ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or (default or "")


def confirm(prompt: str, default: bool = False) -> bool:
    answer = ask(f"{prompt} {'[Y/n]' if default else '[y/N]'}").lower()
    return answer in ("y", "yes") if answer else default


def choose_mode() -> InstallMode:
    options = list(InstallMode) + ["exit"]
    print("\nFedora SwayFX setup\n")
    for index, option in enumerate(options, 1):
        print(f"  {index}. {option.value.replace('-', ' ').title()}")
    choice = int(ask("Choose an action", "1"))
    if choice == len(options):
        raise KeyboardInterrupt
    return options[choice - 1]


def choose_configs() -> ConfigAction:
    print("\nExisting configuration found:")
    print("  1. Backup and replace\n  2. Merge / skip\n  3. Keep existing\n  4. Cancel")
    return [ConfigAction.BACKUP_REPLACE, ConfigAction.SKIP, ConfigAction.KEEP, ConfigAction.CANCEL][int(ask("Choose", "1")) - 1]


def choose_packages(packages: Sequence[PackageSpec]) -> list[PackageSpec]:
    selected = {item.name: item.default for item in packages}
    print("\nCustom package selection (comma-separated numbers, or all/none/default):")
    for index, item in enumerate(packages, 1):
        print(f"  {index:2}. [{'x' if selected[item.name] else ' '}] {item.category}: {item.label} ({item.name})")
    choice = ask("Selection", "default").lower()
    if choice == "all":
        return list(packages)
    if choice == "none":
        return []
    if choice == "default":
        return [item for item in packages if item.default]
    indexes = {int(value.strip()) for value in choice.split(",") if value.strip().isdigit()}
    return [item for index, item in enumerate(packages, 1) if index in indexes]
