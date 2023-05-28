import logging

import click
from flask import Blueprint

from .create_superuser import create_superuser
from .create_superuser import create_superuser_role


cli_bp = Blueprint('superuser', __name__)

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(levelname)s %(message)s')


@cli_bp.cli.command('create')
@click.option('--email')
@click.option('--password')
@click.option('--full_name', default=None)
def createsuperuser(email, password, full_name):
    # create superuser role
    try:
        create_superuser_role()
    except ValueError as e:
        logger.warning(e)
    # create superuser
    try:
        create_superuser(email, password, full_name)
    except ValueError as e:
        logger.warning(e)
   
    
