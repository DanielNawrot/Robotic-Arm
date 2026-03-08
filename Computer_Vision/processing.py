import math

class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def subtract(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def angle_with(self, other) -> float:
        dot_product = self.dot(other)
        mag_product = self.magnitude() * other.magnitude()
        if mag_product == 0:
            return 0.0
        cos_theta = max(-1.0, min(1.0, dot_product / mag_product))  # Clamp for safety
        angle_rad = math.acos(cos_theta)
        return math.degrees(angle_rad)

def vector_substract(v1, v2):
    return Vector(v1.x - v2.x, v1.y - v2.y, v1.z - v2.z)
