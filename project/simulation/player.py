from project.simulation.transform import Transform

class Player:
    def __init__(self, client: 'network.Client'):
        self.client = client
        self.transform = Transform.random()

    def is_dead(self) -> bool:
        return False

    def to_packet(self) -> dict:
        data = self.transform.to_packet()
        return data

    def resurrect(self):
        # health = maxHealth
        # weapon.resetAmmo()
        # ammoReserve = maxAmmoReserve - Weapon.maxAmmo
        self.transform = Transform.random()
