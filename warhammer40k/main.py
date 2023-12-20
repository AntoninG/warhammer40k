import yaml
from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal

from .controllers import Charge, Codex, MathHammer
from .core.exc import WarhammerError
from .hooks import db, repository

# configuration defaults
CONFIG = init_defaults("warhammer40k", "log.logging")
CONFIG["warhammer40k"] = {
    "feed": {
        "repositories_url": "https://api.github.com/repos/BSData/wh40k-10e/git/trees/main"
    },
    "db": {"file": "db/db.json"},
}
CONFIG["log.logging"]["level"] = "debug"


class Warhammer(App):
    """Warhammer 40K primary application."""

    class Meta:
        label = "warhammer40k"

        # configuration defaults
        config_defaults = CONFIG

        config_handler = "yaml"

        # call sys.exit() on close
        exit_on_close = True

        # load additional framework extensions
        extensions = [
            "yaml",
            "colorlog",
            "jinja2",
        ]

        # configuration file suffix
        config_file_suffix = ".yml"

        # set the log handler
        log_handler = "colorlog"

        # set the output handler
        output_handler = "jinja2"

        # register handlers
        handlers = [Charge, MathHammer, Codex]

        hooks = [
            ("post_setup", db.extend_tinydb),
            ("pre_run", repository.fetch_repositories),
        ]


class WarhammerTest(TestApp, Warhammer):
    """A sub-class of Warhammer that is better suited for testing."""

    class Meta:
        label = "warhammer40k"


def main():
    with Warhammer() as app:
        try:
            app.run()

        except AssertionError as e:
            print("AssertionError > %s" % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback

                traceback.print_exc()

        except WarhammerError as e:
            print("WarhammerError > %s" % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback

                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print("\n%s" % e)
            app.exit_code = 0


if __name__ == "__main__":
    main()
