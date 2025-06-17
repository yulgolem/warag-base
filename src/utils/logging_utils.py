from __future__ import annotations

import json
import logging
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


LOG_FILE_PATH = Path("logs/app.jsonl")


class JSONFormatter(logging.Formatter):
    """Format log records as JSON lines."""

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        log: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log.update(record.extra_data)
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        return json.dumps(log, ensure_ascii=False)


class HumanFormatter(logging.Formatter):
    """Simpler human-readable formatter."""

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        return f"{timestamp} | {record.name} | {record.levelname} | {record.getMessage()}"


class LoggerManager:
    """Singleton manager for loggers with console and file handlers."""

    _instance: "LoggerManager" | None = None
    _lock = threading.Lock()

    def __new__(cls) -> "LoggerManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.root_logger = logging.getLogger()
        self.root_logger.setLevel(logging.DEBUG)
        self.root_logger.handlers.clear()

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(HumanFormatter())

        file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONFormatter())

        self.root_logger.addHandler(console_handler)
        self.root_logger.addHandler(file_handler)
        self.loggers: Dict[str, logging.Logger] = {}

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            if cls._instance is not None:
                for handler in logging.getLogger().handlers[:]:
                    handler.close()
                    logging.getLogger().removeHandler(handler)
                cls._instance.loggers.clear()
                cls._instance = None

    def get_logger(self, name: str) -> logging.Logger:
        if name not in self.loggers:
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)
            logger.propagate = True
            logger.handlers.clear()
            self.loggers[name] = logger
        return self.loggers[name]

    def log_with_extra(self, logger_name: str, level: str, message: str, **extra_data: Any) -> None:
        logger = self.get_logger(logger_name)
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(message, extra={"extra_data": extra_data})


def get_agent_logger() -> logging.Logger:
    return LoggerManager().get_logger("agents")


def get_database_logger() -> logging.Logger:
    return LoggerManager().get_logger("database")


def get_ui_logger() -> logging.Logger:
    return LoggerManager().get_logger("ui")


def get_processing_logger() -> logging.Logger:
    return LoggerManager().get_logger("processing")


def log_entity_extraction(chunk_id: str, entities_count: int, processing_time: float, model_used: str) -> None:
    LoggerManager().log_with_extra(
        "agents",
        "info",
        f"Extracted {entities_count} entities from {chunk_id}",
        chunk_id=chunk_id,
        entities_count=entities_count,
        processing_time_ms=processing_time * 1000,
        model_used=model_used,
    )


def log_relationship_analysis(entities_count: int, relationships_found: int, processing_time: float) -> None:
    LoggerManager().log_with_extra(
        "agents",
        "info",
        f"Analyzed {entities_count} entities, found {relationships_found} relationships",
        entities_count=entities_count,
        relationships_found=relationships_found,
        processing_time_ms=processing_time * 1000,
    )


def log_database_operation(operation: str, table: str, records_affected: int, execution_time: float) -> None:
    LoggerManager().log_with_extra(
        "database",
        "info",
        f"{operation} on {table} affected {records_affected} records",
        operation=operation,
        table=table,
        records_affected=records_affected,
        execution_time_ms=execution_time * 1000,
    )


def log_file_processing(file_name: str, chunks_created: int, total_entities: int, processing_time: float) -> None:
    LoggerManager().log_with_extra(
        "processing",
        "info",
        f"Processed {file_name} into {chunks_created} chunks ({total_entities} entities)",
        file_name=file_name,
        chunks_created=chunks_created,
        total_entities=total_entities,
        processing_time_ms=processing_time * 1000,
    )

