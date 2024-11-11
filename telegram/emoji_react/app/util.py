import logging
from fastapi import Request


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_request(request: Request):
    logger.debug(f"Client IP: {request.client.host if request.client else 'N/A'}")
    logger.debug(f"Method: {request.method}")
    logger.debug(f"URL: {request.url}")
    logger.debug(f"Query Params: {request.query_params}")
    logger.debug(f"Path Params: {request.path_params}")
    logger.debug(f"Scope: {request.scope}")
    logger.debug(f"Client IP: {request.client.host if request.client else 'N/A'}")

    logger.debug(f"Headers: {request.headers}")
    for key, value in request.headers.items():
        logger.debug(f"Header - {key}: {value}")
    
    try:
        body = await request.body()
        print(f"Body: {body.decode('utf-8')}")
    except Exception as e:
        print(f"Error reading body: {e}")
    
    try:
        json_data = await request.json()
        print(f"JSON Body: {json_data}")
    except Exception as e:
        print(f"Error parsing JSON: {e}")

    print(f"Scope: {request.scope}")