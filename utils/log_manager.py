import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from utils.data_manager import DataManager

class LogManager:
    """Verwaltet Dokument-Logs für Schüler-Aktivitäten"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    @staticmethod
    def get_ch_timestamp():
        """Gibt aktuellen Schweizer Zeitstempel zurück"""
        return datetime.now(ZoneInfo('Europe/Zurich')).strftime("%Y-%m-%d %H:%M:%S")
    
    def mark_document_as_read(self, document_name: str, student_name: str, student_username: str):
        """Schreibt einen 'Gelesen'-Eintrag in die Log-Datei des Dokuments"""
        log_file = f"documents/{document_name}_log.csv"
        
        log_entry = {
            'timestamp': self.get_ch_timestamp(),
            'student_name': student_name,
            'student_username': student_username,
            'document_name': document_name,
            'action': 'read'
        }
        
        # Laden oder erstellen der Log-Datei
        try:
            log_df = self.data_manager.load_app_data(log_file, initial_value=pd.DataFrame(columns=['timestamp', 'student_name', 'student_username', 'document_name', 'action']))
        except:
            log_df = pd.DataFrame(columns=['timestamp', 'student_name', 'student_username', 'document_name', 'action'])
        
        # Neuen Eintrag hinzufügen
        new_entry = pd.DataFrame([log_entry])
        log_df = pd.concat([log_df, new_entry], ignore_index=True)
        
        # Speichern
        self.data_manager.save_app_data(log_df, log_file)
    
    def get_document_logs(self, document_name: str) -> pd.DataFrame:
        """Gibt alle Logs eines Dokuments zurück"""
        log_file = f"documents/{document_name}_log.csv"
        return self.data_manager.load_app_data(log_file, initial_value=pd.DataFrame(columns=['timestamp', 'student_name', 'student_username', 'document_name', 'action']))