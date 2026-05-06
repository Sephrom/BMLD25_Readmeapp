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
            'quiz_passed_timestamp',
            'quiz_attempts',
            'last_quiz_score'
        ]
        try:
            log_df = self.data_manager.load_app_data(
                log_file,
                initial_value=pd.DataFrame(columns=columns)
            )
            
            # Migriere alte Struktur zur neuen
            if 'action' in log_df.columns:
                # Alte Struktur erkannt - in neue umwandeln
                unique_combos = log_df[['student_name', 'student_username', 'document_name']].drop_duplicates()
                new_rows = []
                
                for _, combo in unique_combos.iterrows():
                    mask = (
                        (log_df['student_username'] == combo['student_username']) &
                        (log_df['document_name'] == combo['document_name'])
                    )
                    old_entries = log_df[mask]
                    
                    # Extrahiere Zeitstempel pro Aktion
                    opened_ts = None
                    read_ts = None
                    
                    if any(old_entries['action'] == 'open'):
                        opened_ts = old_entries[old_entries['action'] == 'open']['timestamp'].iloc[0]
                    if any(old_entries['action'] == 'read'):
                        read_ts = old_entries[old_entries['action'] == 'read']['timestamp'].iloc[0]
                    
                    new_row = {
                        'student_name': combo['student_name'],
                        'student_username': combo['student_username'],
                        'document_name': combo['document_name'],
                        'opened_timestamp': opened_ts,
                        'read_timestamp': read_ts,
                        'quiz_passed_timestamp': None,
                        'quiz_attempts': 0,
                        'last_quiz_score': None
                    }
                    new_rows.append(new_row)
                
                new_df = pd.DataFrame(new_rows)
                self.data_manager.save_app_data(new_df, log_file)
                return new_df
            
            # Fehlerhafte Spalten ergänzen
            for col in columns:
                if col not in log_df.columns:
                    log_df[col] = None
            
            return log_df
        except:
            log_df = pd.DataFrame(columns=columns)
        
        return log_df
    
    def _get_or_create_row(self, log_df: pd.DataFrame, document_name: str, 
                          student_name: str, student_username: str) -> tuple:
        """
        Sucht nach existierendem Eintrag für Schüler+Dokument.
        Falls nicht vorhanden: neu hinzufügen und Index zurückgeben.
        Gibt zurück: (log_df, row_index)
        """
        mask = (
            (log_df['student_username'] == student_username) &
            (log_df['document_name'] == document_name)
        )
        
        if mask.any():
            return log_df, log_df[mask].index[0]
        else:
            # Neue Zeile hinzufügen
            new_row = {
                'student_name': student_name,
                'student_username': student_username,
                'document_name': document_name,
                'opened_timestamp': None,
                'read_timestamp': None,
                'quiz_passed_timestamp': None,
                'quiz_attempts': 0,
                'last_quiz_score': None
            }
            new_df = pd.DataFrame([new_row])
            log_df = pd.concat([log_df, new_df], ignore_index=True)
            return log_df, len(log_df) - 1
    
    def mark_document_as_opened(self, document_name: str, student_name: str, student_username: str):
        """Setzt opened_timestamp wenn noch nicht gesetzt"""
        log_file = f"documents/{document_name}_log.csv"
        
        log_df = self._get_or_create_log_df(log_file)
        log_df, row_idx = self._get_or_create_row(log_df, document_name, student_name, student_username)
        
        # Nur setzen wenn noch nicht vorhanden
        if pd.isna(log_df.loc[row_idx, 'opened_timestamp']):
            log_df.loc[row_idx, 'opened_timestamp'] = self.get_ch_timestamp()
            self.data_manager.save_app_data(log_df, log_file)
    
    def mark_document_as_read(self, document_name: str, student_name: str, student_username: str):
        """Setzt read_timestamp wenn noch nicht gesetzt"""
        log_file = f"documents/{document_name}_log.csv"
        
        log_df = self._get_or_create_log_df(log_file)
        log_df, row_idx = self._get_or_create_row(log_df, document_name, student_name, student_username)
        
        # Nur setzen wenn noch nicht vorhanden
        if pd.isna(log_df.loc[row_idx, 'read_timestamp']):
            log_df.loc[row_idx, 'read_timestamp'] = self.get_ch_timestamp()
            self.data_manager.save_app_data(log_df, log_file)
    
    def record_quiz_attempt(self, document_name: str, student_name: str, student_username: str,
                            score: float, passed: bool):
        """Speichert einen Quizversuch und setzt bei Bestehen den Zeitstempel."""
        log_file = f"documents/{document_name}_log.csv"
        log_df = self._get_or_create_log_df(log_file)
        log_df, row_idx = self._get_or_create_row(log_df, document_name, student_name, student_username)

        attempts = log_df.loc[row_idx, 'quiz_attempts']
        if pd.isna(attempts):
            attempts = 0
        log_df.loc[row_idx, 'quiz_attempts'] = int(attempts) + 1
        log_df.loc[row_idx, 'last_quiz_score'] = score

        if passed and pd.isna(log_df.loc[row_idx, 'quiz_passed_timestamp']):
            log_df.loc[row_idx, 'quiz_passed_timestamp'] = self.get_ch_timestamp()

        self.data_manager.save_app_data(log_df, log_file)
    
    def get_document_logs(self, document_name: str) -> pd.DataFrame:
        """Gibt Log eines Dokuments zurück"""
        log_file = f"documents/{document_name}_log.csv"
        return self._get_or_create_log_df(log_file)