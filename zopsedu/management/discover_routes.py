"""Route Discovery"""
from flask_script import Command
from zopsedu.server import app


class DiscoverRoutes(Command):
    """Discovers all routes registered to the app"""

    # pylint: disable=method-hidden
    def run(self):
        from urllib.parse import unquote
        output = []
        for rule in app.url_map.iter_rules():
            options = {}
            for arg in rule.arguments:
                options[arg] = "[{0}]".format(arg)

            methods = ','.join(rule.methods)
            url = rule.rule
            line = unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
            output.append(line)

        for line in sorted(output):
            print(line)
        # pylint: enable=method-hidden
