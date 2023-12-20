from pytest import raises

from warhammer40k.main import WarhammerTest


def test_warhammer40k():
    # test warhammer40k without any subcommands or arguments
    with WarhammerTest() as app:
        app.run()
        assert app.exit_code == 0
