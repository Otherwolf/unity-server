import random
import datetime

from project import fps_extension
from project.network.client import Client
from project.simulation.player import Player
from project.simulation.transform import Transform


class World:
    max_spawned_items: int = 6  # Maximum items that can be spawned at once

# 	 World bounds - to create random transforms
    min_x: float = -35
    max_x: float = 35
    min_z: float = -70
    max_z: float = 5

    max_items_of_single_type: int = 3   # Maximum items of the particular type that can be present on the scene

    itemId: int = 0  # Item id counter - to generate unique ids
    extension: 'fps_extension.FPSExtension' = None  # Reference to the server extension

    players = []
    items = []

    def __init__(self, extension: 'fps_extension.FPSExtension'):
        self.extension = extension
        random.seed(datetime.datetime.now())

    def get_players(self):
        return self.players

    def spawn_items(self):
        pass
# 	public void spawnItems() {
# 		int itemsCount = rnd.nextInt(maxSpawnedItems);
#
# 		int healthItemsCount = itemsCount / 2;
# 		int hc = 0;
# 		extension.trace("Spawn " + itemsCount + " items.");
#
# 		for (int i = 0; i < itemsCount; i++) {
# 			ItemType itemType = (hc++ < healthItemsCount) ? ItemType.HealthPack : ItemType.Ammo;
# 			if (hasMaxItems(itemType)) {
# 				continue;
# 			}
#
# 			Item item = new Item(itemId++, Transform.randomWorld(), itemType);
# 			items.add(item);
# 			extension.clientInstantiateItem(item);
# 		}
# 	}

    def has_max_items(self, itemType: str) -> bool:
        counter = 0
        for item in self.items:
            if item.get_item_type() == itemType:
                counter += 1
        return counter > self.max_items_of_single_type

    def add_or_respawn_player(self, user: Client) -> bool:
        """
        Add new player if he doesn't exist, or resurrect him if he already added
        :param user:
        :return:
        """
        player = self.get_player(user)
        if player is None:
            player = Player(user)
            self.players.append(player)
            self.extension.client_instantiate_player(player)
            return True
        else:
            player.resurrect()
            self.extension.client_instantiate_player(player)
            return False

    def move_player(self, user: Client, new_transform):
        """
        Trying to move player. If the new transform is not valid, returns null
        :param user:
        :param new_transform:
        :return:
        """
        player = self.get_player(user)
        if player.is_dead():
            return player.transform

        if self.is_valid_new_transform(player, new_transform):
            player.transform.load(new_transform)
            return new_transform

# 	// Check the player intersection with item - to pick it up
# 	private void checkItem(CombatPlayer player, Transform newTransform) {
# 		for (Object itemObj : items.toArray()) {
# 			Item item = (Item) itemObj;
# 			if (item.isClose(newTransform)) {
# 				try {
# 					useItem(player, item);
# 				}
# 				catch (Throwable e) {
# 					extension.trace("Exception using item " + e.getMessage());
# 				}
# 				return;
# 			}
# 		}
# 	}
#
# 	// Applying the item effect and removing the item from World
# 	private void useItem(CombatPlayer player, Item item) {
# 		if (item.getItemType() == ItemType.Ammo) {
# 			if (player.hasMaxAmmoInReserve()) {
# 				return;
# 			}
#
# 			player.addAmmoToReserve(20);
# 			extension.clientUpdateAmmo(player);
# 		}
# 		else if (item.getItemType() == ItemType.HealthPack) {
# 			if (player.hasMaxHealth()) {
# 				return;
# 			}
#
# 			player.addHealth(CombatPlayer.maxHealth / 3);
# 			extension.clientUpdateHealth(player);
# 		}
#
# 		extension.clientRemoveItem(item, player);
# 		items.remove(item);
# 	}
#
    def get_transform(self, user: Client) -> Transform:
        player = self.get_player(user)
        return player.transform

    def is_valid_new_transform(self, player: Player, transform: Transform) -> bool:
        """
        Check if the given transform is valid in terms of collisions, speed hacks etc
        :return:
        """
        return True

    def get_player(self, user: Client):
        """
        Gets the player corresponding to the specified client
        :param user:
        :return:
        """
        for player in self.players:
            if player.client == user:
                return player

#
# 	// Process the shot from client
# 	public void processShot(User fromUser) {
# 		CombatPlayer player = getPlayer(fromUser);
# 		if (player.isDead()) {
# 			return;
# 		}
# 		if (player.getWeapon().getAmmoCount() <= 0) {
# 			return;
# 		}
# 		if (!player.getWeapon().isReadyToFire()) {
# 			return;
# 		}
#
# 		player.getWeapon().shoot();
#
# 		extension.clientUpdateAmmo(player);
# 		extension.clientEnemyShotFired(player);
#
# 		// Determine the intersection of the shot line with any of the other players to check if we hit or missed
# 		for (CombatPlayer pl : players) {
# 			if (pl != player) {
# 				boolean res = checkHit(player, pl);
# 				if (res) {
# 					playerHit(player, pl);
# 					return;
# 				}
#
# 			}
# 		}
#
# 		// if we are here - we missed
# 	}
#
# 	// Performing reload
# 	public void processReload(User fromUser) {
# 		CombatPlayer player = getPlayer(fromUser);
# 		if (player.isDead()) {
# 			return;
# 		}
# 		if (player.getAmmoReserve() == 0) {
# 			return;
# 		}
# 		if (!player.getWeapon().canReload()) {
# 			return;
# 		}
#
# 		player.reload();
# 		extension.clientReloaded(player);
# 		extension.clientUpdateAmmo(player);
# 	}
#
# 	// Checking if the player hits enemy using simple line intersection and
# 	// the known players position and rotation angles
# 	private boolean checkHit(CombatPlayer player, CombatPlayer enemy) {
# 		if (enemy.isDead()) {
# 			return false;
# 		}
#
# 		// First of all checking the line intersection with enemy in top projection
#
# 		double radius = enemy.getCollider().getRadius();
# 		double height = enemy.getCollider().getHeight();
# 		double myAngle = player.getTransform().getRoty();
# 		double vertAngle = player.getTransform().getRotx();
#
# 		// Calculating an angle relatively to X axis anti-clockwise
# 		double normalAngle = normAngle(360 + 90 - myAngle);
#
# 		//Calculating the angle of the line between player and enemy center point
# 		double difx = enemy.getX() - player.getX();
# 		double difz = enemy.getZ() - player.getZ();
#
# 		double ang = 0;
# 		if (difx == 0) {
# 			ang = 90;
# 		}
# 		else {
# 			ang = Math.toDegrees(Math.atan(Math.abs(difz / difx)));
# 		}
#
# 		// Modifying angle depending on the quarter
# 		if (difx <= 0) {
# 			if (difz <= 0) {
# 				ang += 180;
# 			}
# 			else {
# 				ang = 180 - ang;
# 			}
# 		}
# 		else {
# 			if (difz <= 0) {
# 				ang = 360 - ang;
# 			}
# 		}
# 		ang = normAngle(ang);
#
# 		// Calculating min angle to hit
# 		double angDif = Math.abs(ang - normalAngle);
# 		double d = Math.sqrt(difx * difx + difz * difz);
# 		double maxDif = Math.toDegrees(Math.atan(radius / d));
#
# 		if (angDif > maxDif) {
# 			return false;
# 		}
#
# 		// Now calculating the shot in the side projection
#
# 		// Correction value to fit the model visually (as the collider may not totally fit the model height on client)
# 		final double heightCorrection = 0.3;
#
# 		if (vertAngle > 90) {
# 			vertAngle = 360 - vertAngle;
# 		}
# 		else {
# 			vertAngle = -vertAngle;
# 		}
#
# 		double h = d * Math.tan(Math.toRadians(vertAngle));
# 		double dif = enemy.getTransform().getY() - player.getTransform().getY() - h + heightCorrection;
# 		if (dif < 0 || dif > height) {
# 			return false;
# 		}
#
# 		return true;
# 	}
#
# 	private double normAngle(double a) {
# 		if (a >= 360) {
# 			return a - 360;
# 		}
# 		return a;
# 	}
#
# 	// Applying the hit to the player.
# 	// Processing the health and death
# 	private void playerHit(CombatPlayer fromPlayer, CombatPlayer pl) {
# 		pl.removeHealth(20);
#
# 		if (pl.isDead()) {
# 			fromPlayer.addKillToScore();  // Adding frag to the player if he killed the enemy
# 			extension.updatePlayerScore(fromPlayer);
# 			extension.clientKillPlayer(pl, fromPlayer);
# 		}
# 		else {
# 			// Updating the health of the hit enemy
# 			extension.clientUpdateHealth(pl);
# 		}
# 	}
#
# 	// When user lefts the room or disconnects - removing him from the players list
    def user_left(self, user: Client) -> None:
        player = self.get_player(user)
        if not player:
            return
        self.players.remove(player)
