import logging

logger = logging.getLogger('etl_logger')
logging.basicConfig(level=logging.INFO)

c_handler = logging.StreamHandler()
c_handler.setLevel(logging.INFO)

c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)

logger.addHandler(c_handler)