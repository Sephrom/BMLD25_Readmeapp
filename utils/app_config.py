"""Zentrale App-Konfiguration."""

from utils.data_manager import DataManager


def get_data_manager() -> DataManager:
    """Erstellt den DataManager mit der Standardkonfiguration der App."""
    return DataManager(
        fs_protocol="webdav",
        fs_root_folder="BMLD_App_DB",
    )