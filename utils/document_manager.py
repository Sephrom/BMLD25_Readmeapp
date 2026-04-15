import os
import pandas as pd
from utils.data_manager import DataManager

class DocumentManager:
    """Verwaltet Dokumente auf der Switch Drive"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.documents_folder = "documents"
    
    def get_folders(self):
        """Gibt alle Ordner im Dokumente-Verzeichnis zurück"""
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
        except Exception as e:
            print(f"Fehler beim Lesen der Ordner: {e}")
            return []
    
    def get_documents_in_folder(self, folder_name: str):
        """Gibt alle PDF-Dateien in einem Ordner zurück"""
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
        except Exception as e:
            print(f"Fehler beim Lesen der Dokumente: {e}")
            return []
    
    def save_document(self, file_content: bytes, folder_name: str, file_name: str):
        """Speichert eine PDF-Datei in einem Ordner auf der Switch Drive"""
        try:
            path = f"{self.data_manager.fs_root_folder}/{self.documents_folder}/{folder_name}/{file_name}"
            
            # Erstelle Ordner wenn nicht vorhanden
            folder_path = f"{self.data_manager.fs_root_folder}/{self.documents_folder}/{folder_name}"
            if not self.data_manager.fs.exists(folder_path):
                self.data_manager.fs.makedirs(folder_path, exist_ok=True)
            
            # Speichere Datei
            with self.data_manager.fs.open(path, 'wb') as f:
                f.write(file_content)
            
            return True
        except Exception as e:
            print(f"Fehler beim Speichern der Datei: {e}")
            return False
    
    def create_folder(self, folder_name: str):
        """Erstellt einen neuen Ordner"""
        try:
            path = f"{self.data_manager.fs_root_folder}/{self.documents_folder}/{folder_name}"
            self.data_manager.fs.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Fehler beim Erstellen des Ordners: {e}")
            return False
    
    def get_document(self, folder_name: str, file_name: str) -> bytes:
        """Lädt eine PDF-Datei von der Switch Drive"""
        try:
            path = f"{self.data_manager.fs_root_folder}/{self.documents_folder}/{folder_name}/{file_name}"
            
            if self.data_manager.fs.exists(path):
                with self.data_manager.fs.open(path, 'rb') as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"Fehler beim Laden der Datei: {e}")
            return None
    
    def delete_document(self, folder_name: str, file_name: str) -> bool:
        """Löscht eine PDF-Datei von der Switch Drive"""
        try:
            path = f"{self.data_manager.fs_root_folder}/{self.documents_folder}/{folder_name}/{file_name}"
            
            if self.data_manager.fs.exists(path):
                self.data_manager.fs.rm(path)
                return True
            return False
        except Exception as e:
            print(f"Fehler beim Löschen der Datei: {e}")
            return False


