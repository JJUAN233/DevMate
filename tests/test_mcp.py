import urllib.request
from devmate.logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    try:
        req = urllib.request.Request('http://localhost:8001/mcp', method='POST')
        urllib.request.urlopen(req)
    except Exception as e:
        logger.error(e.read().decode())
