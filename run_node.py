import logging

import uvicorn

from ilc_core.logging_config import configure_logging


configure_logging()
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("node_daemon_starting")
    logger.info("node_daemon_api_endpoint url=http://127.0.0.1:8000")
    logger.info("node_daemon_docs_endpoint url=http://127.0.0.1:8000/docs")
    
    # Run the FastAPI app from the ilc_core.server module
    uvicorn.run("ilc_core.server:app", host="127.0.0.1", port=8000, reload=True)
