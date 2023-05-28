import sys

from logger import logger
from parse_args import parse_args


def waiting(service_name: str, checking_func: callable, *, default_host: str = None, default_port: str = None,
            func_args: dict | None = None):
    args = parse_args(sys.argv, ('host', 'port'))
    host = args.get('host', None) or default_host
    port = args.get('port', None) or default_port
    if not port.isdigit():
        port = default_port
    logger.info(f'Check {service_name} connection (host={host}, port={port})...')
    if func_args is None:
        func_args = {}
    checking_func(host, port, **func_args)
    logger.info(f'{service_name} is ready!')


