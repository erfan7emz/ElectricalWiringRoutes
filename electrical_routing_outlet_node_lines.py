from ..utils import inch_to_base_unit, create_polygon, create_base_object
from ..coord import min_x_coord, max_x_coord, min_y_coord, max_y_coord
from shapely.geometry import Point


MINIMUM_BAY = inch_to_base_unit(12.0)
WIRE_SPACE = inch_to_base_unit(1.0)

WIRE_WIDTH = inch_to_base_unit(0.1)

# BUILDING_LAYER is a constant for the input layer name
BUILDING_LAYER1 = "joistHole"
BUILDING_LAYER2 = "joist"
OBJECT = "outlet"

# ANNOTATIONS_LAYER is a constant for the output layer name
ANNOTATIONS_LAYER = "annotations/outletNodeLines"

points_in_outlet_range = []


class OutletNodeLines:
    def __init__(self, variation, params={}):
        self.variation = variation
        self.params = params
        self.generated_layers = self.params["layers"]
        self.changes = set()

    points_in_outlet_range = []

    def generate(self):
        interior_objects1 = self.generated_layers[BUILDING_LAYER1]["objects"]
        interior_objects2 = self.generated_layers[BUILDING_LAYER2]["objects"]
        outlets = self.generated_layers[OBJECT]["objects"]
        mid_panel_x = 0
        new_layer = self.variation.add_layer(ANNOTATIONS_LAYER)
        self.changes.add(ANNOTATIONS_LAYER)
        for outlet in outlets:
            points_in_outlet_range = []

            min_panel_x = min_x_coord(outlet)
            max_panel_x = max_x_coord(outlet)
            min_panel_y = min_y_coord(outlet)
            max_panel_y = max_y_coord(outlet)
            mid_panel_x = (min_panel_x + max_panel_x) / 2
            mid_panel_y = (min_panel_y + max_panel_y) / 2

            # check hole
            for obj in interior_objects1:
                min_x = min_x_coord(obj)
                max_x = max_x_coord(obj)
                min_y = min_y_coord(obj)
                max_y = max_y_coord(obj)

                # verical joist hole
                if max_x - min_x <= max_y - min_y and min_y <= mid_panel_y <= max_y:
                    curr = min_x + WIRE_SPACE
                    min_distance_x = abs(curr - mid_panel_x)
                    x_coord = curr
                    while curr + WIRE_SPACE + WIRE_WIDTH <= max_x:
                        if abs(curr - mid_panel_x) < min_distance_x:
                            min_distance_x = abs(curr - mid_panel_x)
                            x_coord = curr
                        curr = curr + WIRE_SPACE + WIRE_WIDTH
                    points_in_outlet_range.append(
                        Point(x_coord, mid_panel_y))

                # horizontal joist hole
                elif min_x <= mid_panel_x <= max_x:
                    # add the wires
                    curr = max_y - WIRE_SPACE
                    min_distance_y = abs(curr - mid_panel_y)
                    y_coord = curr

                    while curr - WIRE_SPACE - WIRE_WIDTH >= min_y:
                        if abs(curr - mid_panel_y) < min_distance_y:
                            min_distance_y = abs(curr - mid_panel_y)
                            y_coord = curr
                        curr = curr - WIRE_SPACE - WIRE_WIDTH
                    points_in_outlet_range.append(
                        Point(mid_panel_x, y_coord))

            # joist bay
            for i in range(len(interior_objects2) - 1):
                obj = interior_objects2[i]
                next_obj = interior_objects2[i+1]

                min_x = max_x_coord(obj)
                max_x = min_x_coord(next_obj)
                min_y = min(min_y_coord(obj), min_y_coord(next_obj))
                max_y = max(max_y_coord(obj), max_y_coord(next_obj))

                # if bay is at least MINIMUM_BAY, create joist bay polygon
                # vertical bay
                if max_x - min_x >= MINIMUM_BAY and max_x - min_x <= max_y - min_y and min_y <= mid_panel_y <= max_y:
                    # add the wires
                    curr = min_x + WIRE_SPACE
                    min_distance_x = abs(curr - mid_panel_x)
                    x_coord = curr
                    while curr + WIRE_SPACE + WIRE_WIDTH <= max_x:
                        if abs(curr - mid_panel_x) < min_distance_x:
                            min_distance_x = abs(curr - mid_panel_x)
                            x_coord = curr
                        curr = curr + WIRE_SPACE + WIRE_WIDTH
                    points_in_outlet_range.append(
                        Point(x_coord, mid_panel_y))
                    continue

                # horizontal
                min_x = min(min_x_coord(obj), min_x_coord(next_obj))
                max_x = max(max_x_coord(obj), max_x_coord(next_obj))
                min_y = max_y_coord(next_obj)
                max_y = min_y_coord(obj)

                width = max_y - min_y
                if width >= MINIMUM_BAY and max_x - min_x > width and min_x <= mid_panel_x <= max_x:
                    # add the wires
                    curr = max_y - WIRE_SPACE
                    min_distance_y = abs(curr - mid_panel_y)
                    y_coord = curr

                    while curr - WIRE_SPACE - WIRE_WIDTH >= min_y:
                        if abs(curr - mid_panel_y) < min_distance_y:
                            min_distance_y = abs(curr - mid_panel_y)
                            y_coord = curr
                        curr = curr - WIRE_SPACE - WIRE_WIDTH
                    points_in_outlet_range.append(
                        Point(mid_panel_x, y_coord))

            # find the closest point in outlet range
            min_distance = points_in_outlet_range[0].distance(
                Point(mid_panel_x, mid_panel_y))
            x_coord = points_in_outlet_range[0].x
            y_coord = points_in_outlet_range[0].y

            for point in points_in_outlet_range:
                if point.distance(Point(mid_panel_x, mid_panel_y)) < min_distance:
                    min_distance = point.distance(
                        Point(mid_panel_x, mid_panel_y))
                    x_coord = point.x
                    y_coord = point.y

            wire_coords = []
            if abs(mid_panel_x - x_coord) < abs(mid_panel_y - y_coord):
                wire_coords = [
                    mid_panel_x, mid_panel_y,
                    mid_panel_x + WIRE_WIDTH, mid_panel_y,
                    x_coord + WIRE_WIDTH, y_coord,
                    x_coord, y_coord
                ]
            else:
                wire_coords = [
                    mid_panel_x, mid_panel_y,
                    x_coord, y_coord,
                    x_coord, y_coord + WIRE_WIDTH,
                    mid_panel_x, mid_panel_y + WIRE_WIDTH
                ]

            bay_line = create_polygon(wire_coords)

            wire_base_object = create_base_object(
                bay_line, properties={"color": "red"}
            )
            self.variation.add_object(ANNOTATIONS_LAYER, wire_base_object)
