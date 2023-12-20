from cement import Controller, ex
from warhammer_stats import PMFCollection


class Charge(Controller):
    class Meta:
        label = "charge"
        stacked_type = "embedded"
        stacked_on = "base"

    @ex(
        help="Test charge",
        arguments=[
            (["charge"], {"action": "store", "type": int}),
            (["--modifier", "-m"], {"action": "store", "default": 0, "type": int}),
            (["--rerolls", "-r"], {"action": "store_true"}),
        ],
    )
    def charge(self):
        charge = self.app.pargs.charge
        modifier = self.app.pargs.modifier
        is_rerolling = self.app.pargs.rerolls

        dices = PMFCollection.mdn(2, 6)
        probability = sum(dices.convolve().roll(modifier).values[charge:])
        if is_rerolling:
            probability = probability + (1 - probability) * probability

        self.app.log.info(f"{round(probability * 100, 2)}% success chance")
