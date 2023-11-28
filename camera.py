import numpy as np


class Camera:
    def __init__(
        self, position=[0, -2, -10], f=3, alpha=100, beta=100, u=400, v=300
    ) -> None:
        self.position = position
        self.f = f
        self.alpha = alpha
        self.beta = beta
        self.u0 = u
        self.v0 = v
        self.angle_h = 0
        self.angle_v = 0
        self.K = np.array(
            [[self.f * self.alpha, 0, self.u0], [0, self.f * self.beta, self.v0]]
        )
