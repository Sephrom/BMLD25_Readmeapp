import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from utils.data_manager import DataManager

class LogManager:
    """Verwaltet Dokument-Logs für Schüler-Aktivitäten (spaltenweise Struktur)"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    @staticmethod
    def get_ch_timestamp():
        """Gibt aktuellen Schweizer Zeitstempel zurück"""
        return datetime.now(ZoneInfo('Europe/Zurich')).strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_or_create_log_df(self, log_file: str) -> pd.DataFrame:
        """Lade Log-Datei oder erstelle neue mit korrekter Struktur"""
        columns = [
            'student_name',
            'student_username',
            'document_name',
            'opened_timestamp',
            'read_timestamp',
            'quiz_passed_timestamp'
        ]
        try:
            log_df = self.data_manager.load_app_data(
                log_file,
                initial_value=pd.DataFrame(columns=columns)
            )
        except:
            log_df = pd.DataFrame(columns=columns)
        
        return log_df
    
    def _get_or_create_row(self, log_df: pd.DataFrame, document_name: str, 
                          student_name: str, student_username: str) -> int:
        """
        Sucht nach existierendem Eintrag für Schüler+Dokument.
        Falls nicht vorhanden: neu hinzufügen und Index zurückgeben.
        """
        mask = (
            (log_df['student_username'] == student_username) &
            (log_df['document_name'] == document_name)
        )
        
        if mask.any():
            return log_df[mask].index[0]
        else:
            # Neue Zeile hinzufügen
            new_row = {
                'student_name': student_name,
                'student_username': student_username,
                'document_name': document_name,
                'opened_timestamp': None,
                'read_timestamp': None,
                'quiz_passed_timestamp': None
            }
            new_df = pd.DataFrame([new_row])
            log_df = pd.concat([log_df, new_df], ignore_index=True)
            return len(log_df) - 1
    
    def mark_document_as_opened(self, document_name: str, student_name: str, student_username: str):
        """Setzt opened_timestamp wenn noch nicht gesetzt"""
        log_file = f"documents/{document_name}_log.csv"
        
        log_df = self._get_or_create_log_df(log_file)
        row_idx = self._get_or_create_row(log_df, document_name, student_name, student_username)
        
        # Nur setzen wenn noch nicht vorhanden
        if pd.isna(log_df.loc[row_idx, 'opened_timestamp']):
            log_df.loc[row_idx, 'opened_timestamp'] = self.get_ch_timestamp()
            self.data_manager.save_app_data(log_df, log_file)
    
    def mark_document_as_read(self, document_name: str, student_name: str, student_username: str):
        """Setzt read_timestamp wenn noch nicht gesetzt"""
        log_file = f"documents/{document_name}_log.csv"
        
        log_df = self._get_or_create_log_df(log_file)
        row_idx = self._get_or_create_row(log_df, document_name, student_name, student_username)
        
        # Nur setzen wenn noch nicht vorhanden
        if pd.isna(log_df.loc[row_idx, 'read_timestamp']):
            log_df.loc[row_idx, 'read_timestamp'] = self.get_ch_timestamp()
            self.data_manager.save_app_data(log_df, log_file)
    
    def mark_quiz_as_passed(self, document_name: str, student_name: str, student_username: str):
        """Setzt quiz_passed_timestamp wenn noch nicht gesetzt"""
        log_file = f"documents/{document_name}_log.csv"
        
        log_df = self._get_or_create_log_df(log_file)
        row_idx = self._get_or_create_row(log_df, document_name, student_name, student_username)
        
        # Nur setzen wenn noch nicht vorhanden
        if pd.isna(log_df.loc[row_idx, 'quiz_passed_timestamp']):
            log_df.loc[row_idx, 'quiz_passed_timestamp'] = self.get_ch_timestamp()
            self.data_manager.save_app_data(log_df, log_file)
    
    def get_document_logs(self, document_name: str) -> pd.DataFrame:
        """Gibt Log eines Dokuments zurück"""
        log_file = f"documents/{document_name}_log.csv"
        return self._get_or_create_log_df(log_file)