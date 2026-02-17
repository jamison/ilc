import logging

import uvicorn

from ilc_core.logging_config import configure_logging


configure_logging()
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("node_daemon_starting")
    logger.info("node_daemon_api_endpoint url=http://127.0.0.1:8000")
    logger.info("node_daemon_docs_endpoint url=http://127.0.0.1:8000/docs")
    
    # Run FastAPI app via factory to avoid server-module import side effects.
    uvicorn.run("ilc_core.server:create_app", factory=True, host="127.0.0.1", port=8000, reload=True)
