import logging

logging.basicConfig(
    filename='logfile.log',
    level=logging.ERROR,
    format='%(asctime)s %(name)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

extractor_logger = logging.getLogger('EXTRACTOR')
loader_logger = logging.getLogger('LOADER')
