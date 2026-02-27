
import logging
import sys
from contextvars import ContextVar
import uuid

# Context variable to store the correlation ID for the current request context
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="-")

class CorrelationIdFormatter(logging.Formatter):
    def format(self, record):
        record.correlation_id = correlation_id_ctx.get()
        return super().format(record)

def setup_logging():
    log_format = "%(asctime)s - %(levelname)s - [%(correlation_id)s] - %(name)s - %(message)s"
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
            
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(CorrelationIdFormatter(log_format))
    root_logger.addHandler(console_handler)
    
    # File handler (optional, but requested for async_sync)
    # We'll use a standard file for general logs if needed, 
    # but the task specifically mentioned async_sync.py file-based logging.
    
    # Silent noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

def get_logger(name):
    return logging.getLogger(name)
