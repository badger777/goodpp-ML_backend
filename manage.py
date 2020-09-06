from flask import abort, request
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import create_app, db
from app.models import User, Ppcam, Pet, Pad, PetRecord
# from config import config as Config
import os
import logging
import sys

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# flask-script and migrate be initialized out of __init__
manager = Manager(app)
migrate = Migrate(app, db)

# IP Whitelist
ip_whitelist = ['172.26.0.1']

@app.before_request
def limit_remote_addr():
    if request.remote_addr not in ip_whitelist:
        logging.error("forbidden ip request")
        abort(403) # Forbidden

# def make_shell_context():
#     return dict(app=app, db=db)

# manager.add_command('shell', Shell(make_context=make_shell_context))

manager.add_command('db', MigrateCommand)

@manager.command
def run():
    app.run(host='0.0.0.0')

@manager.command
def recreate_db():
    "Recreate a local db. do not use this on production"
    db.drop_all()
    db.create_all()
    db.session.commit()

@manager.option(
    '-n',
    '--number-users',
    default=10,
    type=int,
    help='Num of each model type to create',
    dest='number_users'
)
def add_fake_data(number_users):
    "Adds fake data to the db"
    User.generate_fake(count=number_users)
    Ppcam.generate_fake(count=number_users)
    Pet.generate_fake(count=number_users)
    Pad.generate_fake(count=number_users)
    PetRecord.generate_fake(count=number_users)

@manager.command
def setup_prod():
    "Runs the set-up needed for local dev"
    setup_general()

def setup_general():
    "Runs the set-up needed for both local dev and production"
    
if __name__ == '__main__':
    manager.run()
