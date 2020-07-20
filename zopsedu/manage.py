"""Zopsedu Management Commands"""
from flask_script import Manager

from zopsedu.management.insert_initial_data import InsertInitialData
from zopsedu.management.discover_routes import DiscoverRoutes
from zopsedu.server import app

if __name__ == "__main__":
    MANAGER = Manager(app)
    MANAGER.add_command('insert_data', InsertInitialData())
    MANAGER.add_command('discover_routes', DiscoverRoutes())
    MANAGER.run()
