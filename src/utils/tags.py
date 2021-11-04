import json

class Client:
    def __init__(self):
        pass

    def auth_by_email(self, d, e, pw):
        return "{\"d\":\"" + d + "\",\"ty\":\"sin\",\"e\":\"" + \
            e + "\",\"pw\":\"" + pw + "\"}"

    def acfl(self, t, uo):
        return "{\"t\":\"" + t + "\", \"ty\":\"acfl\", \"uo\":\"" + uo + "\"}"

    def acpc(self, t, uo, fp):
        return "{\"t\":\"" + t + "\", \"ty\":\"acpc\", \"uo\":\"" + \
            uo + "\", \"fp\":\"" + fp + "\"}"

    def ac(self, fp):
        return "{\"ty\":\"ac\", \"fp\":\"" + fp + "\"}"

    def pmc(self, fp, tx):
        return json.dumps({"ty": "pmc", "m": {"fp": fp, "tx": tx}})

    def acc(self, t, uo):
        return "{\"t\":\"" + t + "\", \"ty\":\"acc\", \"uo\":\"" + uo + "\"}"

    def cmc(self, tx):
        return json.dumps({"ty": "cmc", "m": {"tx": tx}})

    def gup(self, uo):
        return "{\"ty\":\"gup\", \"uo\":\"" + uo + "\"}"
