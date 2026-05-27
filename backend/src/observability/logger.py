import json
import logging
from datetime import datetime
from pathlib import Path
from src.config import Config

class TelemetryLogger:
    def __init__(self, log_file: Path = Config.LOGS_DIR / "telemetry.jsonl"):
        self.log_file = log_file
        # Set up a standard python logger that only writes to file
        self._logger = logging.getLogger("telemetry")
        self._logger.setLevel(logging.INFO)
        
        # Prevent adding multiple handlers if instantiated multiple times
        if not self._logger.handlers:
            handler = logging.FileHandler(self.log_file)
            handler.setFormatter(logging.Formatter('%(message)s'))
            self._logger.addHandler(handler)
            self._logger.propagate = False

    def log_event(self, trace_id: str, event_type: str, payload: dict):
        """
        Logs a structured telemetry event to the JSONL log file.
        """
        event = {
            "trace_id": trace_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "payload": payload
        }
        
        try:
            # We use the python logger to handle concurrent writes safely via its threading locks
            self._logger.info(json.dumps(event))
        except Exception as e:
            # Fallback to standard logging if telemetry fails, to avoid crashing the app
            logging.error(f"Failed to write telemetry event: {e}")

# Global singleton for easy import
telemetry_logger = TelemetryLogger()
