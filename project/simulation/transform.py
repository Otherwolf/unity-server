import random
import math


class Transform:
    x: float
    y: float
    z: float

    rotx: float
    roty: float
    rotz: float

    time_stamp: float = 0

    def __init__(self, x: float, y:float, z: float, rotx: float, roty: float, rotz: float):
        self.x = x
        self.y = y
        self.z = z

        self.rotx = rotx
        self.roty = roty
        self.rotz = rotz

    @classmethod
    def random(cls):
        """
         Create random transform choosing from the predefined spawnPoints list
        :return:
        """
        spawn_points = cls.get_spawn_points()
        i = random.randrange(len(spawn_points))
        return spawn_points[i]

    @classmethod
    def get_spawn_points(cls) -> list:
        """
        Create random transform using the specified bounds
        :return:
        """
        spawn_points = []
        spawn_points.append(Transform(25, 6, 3, 0, 0, 0))
        spawn_points.append(Transform(-24, 6, -20, 0, 0, 0))
        spawn_points.append(Transform(18, 6, -63, 0, 0, 0))
        return spawn_points

    def random_world(self):
        pass

    def distance_to(self, transform) -> float:
        """
        Calculate distance to another transform
        :param transform:
        :return:
        """
        dx = (self.x - transform.x) ** 2
        dy = (self.y - transform.y) ** 2
        dz = (self.z - transform.z) ** 2
        return math.sqrt(dx + dy + dz)

    def load(self, another) -> None:
        """
        Copy another transform to this one
        :param transform:
        :return:
        """
        self.x = another.x
        self.y = another.y
        self.z = another.z

        self.rotx = another.rotx
        self.roty = another.roty
        self.rotz = another.rotz

        self.time_stamp = another.time_stamp

    @staticmethod
    def from_packet(data: dict):
        pos = data.get('pos')
        rot = data.get('rot', {'x': 0, 'y': 0, 'z': 0})
        transform = Transform(**pos, rotx=rot['x'], roty=rot['y'], rotz=rot['z'])
        transform.time_stamp = data.get('t', 0)
        # todo: добавить time stamp и ротацию
        return transform


    def to_packet(self):
        data = dict(
            pos={'x': self.x, 'y': self.y, 'z': self.z},
            rot={'x': self.rotx, 'y': self.roty, 'z': self.rotz},
            t=self.time_stamp
        )
        return data
