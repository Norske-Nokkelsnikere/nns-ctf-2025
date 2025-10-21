from dataclasses import dataclass

@dataclass(eq=True, frozen=True)
class Point:
    x: float
    y: float

    def __hash__(self):
        return hash((self.x, self.y))

def rotate_to_be_closest_to_y_axis(main_point, secondary_point):
    if main_point.x <= 0.5 and main_point.y >= main_point.x and main_point.y <= 1 - main_point.x:
        return main_point, secondary_point
    elif main_point.x >= 0.5 and main_point.y >= 1-main_point.x and main_point.y <= main_point.x:
        # Rotate across x = 0.5
        return Point(1 - main_point.x, main_point.y), Point(1 - secondary_point.x, secondary_point.y)
    elif main_point.y <= 0.5 and main_point.x >= main_point.y and main_point.x <= 1 - main_point.y:
        # Rotate 90 degrees
        return Point(main_point.y, 1-main_point.x), Point(secondary_point.y, 1-secondary_point.x)
    else:
        #Rotate 90 degrees anticlockwise
        return Point(1-main_point.y, main_point.x), Point(1-secondary_point.y, secondary_point.x)

def find_y_of_circle_on_x_axis(p1, p2):
    if p1.y == p2.y:
        return None
    return (p1.x**2 + p1.y**2 - p2.x**2 - p2.y**2)/(2*(p1.y - p2.y))

def are_equidistant_to_point_on_closest_line(main_point, secondary_point):
    main_point, secondary_point = rotate_to_be_closest_to_y_axis(main_point, secondary_point)
    y_mid = find_y_of_circle_on_x_axis(main_point, secondary_point)
    return y_mid is not None and y_mid >= 0 and y_mid <= 1


