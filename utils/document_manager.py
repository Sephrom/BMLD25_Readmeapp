import os
from utils.data_manager import DataManager


class DocumentManager:
    """Verwaltet Dokumente auf der Switch Drive"""

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.documents_folder = "documents"
        self.last_error = None

    @staticmethod
    def _validate_name(name: str, name_type: str = "folder") -> bool:
        if not name or not isinstance(name, str):
            return False
        if ".." in name or "/" in name or "\\" in name:
            return False
        if name.strip() == "":
            return False
        return True

    def _clear_error(self) -> None:
        """Setzt den letzten Fehler auf None"""
        self.last_error = None

    def _set_error(self, message: str, exc: Exception = None) -> None:
        """Speichert eine lesbare Fehlermeldung"""
        if exc:
            self.last_error = f"{message} [{type(exc).__name__}]"
        else:
            self.last_error = message

    def get_last_error(self) -> str | None:
        """Gibt die letzte Fehlermeldung zurück oder None"""
        return self.last_error

    def get_folders(self):
        self._clear_error()
        try:
            path = f"{self.data_manager.fs_root_folder}/{self.documents_folder}"
            folders = []

            if self.data_manager.fs.exists(path):
                for item in self.data_manager.fs.listdir(path):
                    item_path = item['name']
                    if self.data_manager.fs.isdir(item_path):
                        folder_name = os.path.basename(item_path)
                        folders.append(folder_name)
            return folders
        except Exception as exc:
            self._set_error("Ordner konnten nicht geladen werden.", exc)
            return []

    def get_documents_in_folder(self, folder_name: str):
        self._clear_error()
        if not self._validate_name(folder_name, "folder"):
            return []

        try:
            path = f"{self.data_manager.fs_root_folder}/{self.documents_folder}/{folder_name}"
            documents = []

            if self.data_manager.fs.exists(path):
                for item in self.data_manager.fs.listdir(path):
                    item_path = item['name']
                    if item_path.endswith('.pdf'):
                        doc_name = os.path.basename(item_path)
                        documents.append(doc_name)
            return documents
        except Exception as exc:
            self._set_error("Dokumente konnten nicht geladen werden.", exc)
            return []

    def save_document(self, file_content: bytes, folder_name: str, file_name: str):
        self._clear_error()
        if not self._validate_name(folder_name, "folder"):
            self._set_error("Zielordner ist ungueltig.")
            return False
        if not self._validate_name(file_name, "file"):
            self._set_error("Dateiname ist ungueltig.")
            return False

        try:
            file_name = os.path.basename(file_name)
            path = f"{self.data_manager.fs_root_folder}/{self.documents_folder}/{folder_name}/{file_name}"

            folder_path = f"{self.data_manager.fs_root_folder}/{self.documents_folder}/{folder_name}"
            if not self.data_manager.fs.exists(folder_path):
                self.data_manager.fs.makedirs(folder_path, exist_ok=True)

            with self.data_manager.fs.open(path, 'wb') as f:
                f.write(bytes(file_content))

            return True
        except Exception as exc:
            self._set_error("Dokument konnte nicht gespeichert werden.", exc)
            return False

    def create_folder(self, folder_name: str):
        self._clear_error()
        if not self._validate_name(folder_name, "folder"):
            self._set_error("Ordnername ist ungueltig.")
            return False

        try:
            path = f"{self.data_manager.fs_root_folder}/{self.documents_folder}/{folder_name}"
            self.data_manager.fs.makedirs(path, exist_ok=True)
            return True
        except Exception as exc:
            self._set_error("Ordner konnte nicht erstellt werden.", exc)
            return False

    def load_classes(self) -> list:
        """Laedt gespeicherte Klassen aus der zentralen Klassenliste."""
        try:
            data = self.data_manager.load_app_data("classes.json", initial_value={"classes": []})
            return sorted(set(data.get("classes", [])))
        except Exception:
            return []

    def save_classes(self, classes: list) -> bool:
        """Speichert die zentrale Klassenliste."""
        try:
            clean_classes = sorted({
                class_name.strip()
                for class_name in classes
                if self._validate_name(class_name, "class")
            })
            self.data_manager.save_app_data({"classes": clean_classes}, "classes.json")
            return True
        except Exception as exc:
            self._set_error("Klassenliste konnte nicht gespeichert werden.", exc)
            return False

    def create_class(self, class_name: str) -> bool:
        """Erstellt eine Klasse in der Klassenliste und als Dokumentordner."""
        self._clear_error()
        if not self._validate_name(class_name, "class"):
            self._set_error("Klassenname ist ungueltig.")
            return False

        class_name = class_name.strip()
        classes = self.load_classes()
        if class_name not in classes:
            classes.append(class_name)

        return self.save_classes(classes) and self.create_folder(class_name)

    def get_document(self, folder_name: str, file_name: str) -> bytes:
        self._clear_error()
        if not self._validate_name(folder_name, "folder"):
            return None
        if not self._validate_name(file_name, "file"):
            return None

        try:
            file_name = os.path.basename(file_name)
            path = f"{self.data_manager.fs_root_folder}/{self.documents_folder}/{folder_name}/{file_name}"

            if self.data_manager.fs.exists(path):
                with self.data_manager.fs.open(path, 'rb') as f:
                    return f.read()
            return None
        except Exception as exc:
            self._set_error("Dokument konnte nicht geladen werden.", exc)
            return None

    def load_quiz(self, folder_name: str, document_name: str) -> dict:
        if not self._validate_name(folder_name, "folder"):
            return {"questions": []}
        if not self._validate_name(document_name, "file"):
            return {"questions": []}

        quiz_file = f"documents/{folder_name}/{document_name}_quiz.json"
        return self.data_manager.load_app_data(quiz_file, initial_value={"questions": []})

    def save_quiz(self, folder_name: str, document_name: str, quiz_data: dict) -> bool:
        self._clear_error()
        if not self._validate_name(folder_name, "folder"):
            return False
        if not self._validate_name(document_name, "file"):
            return False

        quiz_file = f"documents/{folder_name}/{document_name}_quiz.json"
        try:
            self.data_manager.save_app_data(quiz_data, quiz_file)
            return True
        except Exception as exc:
            self._set_error("Quiz-Daten konnten nicht gespeichert werden.", exc)
            return False

    def load_document_meta(self, folder_name: str, document_name: str) -> dict:
        if not self._validate_name(folder_name, "folder"):
            return {"due_date": None}
        if not self._validate_name(document_name, "file"):
            return {"due_date": None}

        meta_file = f"documents/{folder_name}/{document_name}.meta.json"
        return self.data_manager.load_app_data(meta_file, initial_value={"due_date": None})

    def save_document_meta(self, folder_name: str, document_name: str, meta_data: dict) -> bool:
        self._clear_error()
        if not self._validate_name(folder_name, "folder"):
            self._set_error("Zielordner ist ungueltig.")
            return False
        if not self._validate_name(document_name, "file"):
            self._set_error("Dateiname ist ungueltig.")
            return False

        meta_file = f"documents/{folder_name}/{document_name}.meta.json"
        try:
            self.data_manager.save_app_data(meta_data, meta_file)
            return True
        except Exception as exc:
            self._set_error("Dokument-Metadaten konnten nicht gespeichert werden.", exc)
            return False

    def quiz_exists(self, folder_name: str, document_name: str) -> bool:
        self._clear_error()
        if not self._validate_name(folder_name, "folder"):
            return False
        if not self._validate_name(document_name, "file"):
            return False

        quiz_file = f"documents/{folder_name}/{document_name}_quiz.json"
        try:
            return self.data_manager.fs.exists(f"{self.data_manager.fs_root_folder}/{quiz_file}")
        except Exception as exc:
            self._set_error("Quiz-Status konnte nicht überprüft werden.", exc)
            return False

    def delete_document(self, folder_name: str, file_name: str) -> bool:
        self._clear_error()
        if not self._validate_name(folder_name, "folder"):
            return False
        if not self._validate_name(file_name, "file"):
            return False

        try:
            file_name = os.path.basename(file_name)
            path = f"{self.data_manager.fs_root_folder}/{self.documents_folder}/{folder_name}/{file_name}"

            if self.data_manager.fs.exists(path):
                self.data_manager.fs.rm(path)

                meta_file = f"documents/{folder_name}/{file_name}.meta.json"
                meta_path = f"{self.data_manager.fs_root_folder}/{meta_file}"
                if self.data_manager.fs.exists(meta_path):
                    self.data_manager.fs.rm(meta_path)

                quiz_file = f"documents/{folder_name}/{file_name}_quiz.json"
                quiz_path = f"{self.data_manager.fs_root_folder}/{quiz_file}"
                if self.data_manager.fs.exists(quiz_path):
                    self.data_manager.fs.rm(quiz_path)

                classes_file = f"documents/{folder_name}/{file_name}.classes.json"
                classes_path = f"{self.data_manager.fs_root_folder}/{classes_file}"
                if self.data_manager.fs.exists(classes_path):
                    self.data_manager.fs.rm(classes_path)

                logs_file = f"documents/{folder_name}/{file_name}_log.csv"
                logs_path = f"{self.data_manager.fs_root_folder}/{logs_file}"
                if self.data_manager.fs.exists(logs_path):
                    self.data_manager.fs.rm(logs_path)

                return True
            return False
        except Exception as exc:
            self._set_error("Dokument konnte nicht gelöscht werden.", exc)
            return False

    def load_class_assignments(self, folder_name: str, document_name: str) -> dict:
        if not self._validate_name(folder_name, "folder"):
            return {"assigned_classes": []}
        if not self._validate_name(document_name, "file"):
            return {"assigned_classes": []}

        classes_file = f"documents/{folder_name}/{document_name}.classes.json"
        return self.data_manager.load_app_data(classes_file, initial_value={"assigned_classes": []})

    def save_class_assignments(self, folder_name: str, document_name: str, classes_list: list) -> bool:
        self._clear_error()
        if not self._validate_name(folder_name, "folder"):
            self._set_error("Ordnername ist ungueltig.")
            return False
        if not self._validate_name(document_name, "file"):
            self._set_error("Dateiname ist ungueltig.")
            return False

        classes_file = f"documents/{folder_name}/{document_name}.classes.json"
        try:
            self.data_manager.save_app_data({"assigned_classes": classes_list}, classes_file)
            return True
        except Exception as exc:
            self._set_error("Klassenzuordnung konnte nicht gespeichert werden.", exc)
            return False

    def get_all_classes_from_students(self) -> list:
        try:
            creds = self.data_manager.load_app_data('credentials.yaml', initial_value={"usernames": {}})
            classes = set(self.load_classes())
            classes.update(self.get_folders())
            for user_data in creds.get("usernames", {}).values():
                user_class = user_data.get("class")
                if user_class:
                    classes.add(user_class)
            return sorted(list(classes))
        except Exception:
            return []
