from self_driving_lab_demo import SelfDrivingLabDemo


class SelfDrivingLab(SelfDrivingLabDemo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def bounds(self):
        mx = self.max_power
        return dict(
            R=[0, mx],
            Y=[0, mx],
            B=[0, mx],
            atime=[0, 255],
            astep=[0, 65534],
        )


sdl = SelfDrivingLab(simulation=True)

1 + 1
