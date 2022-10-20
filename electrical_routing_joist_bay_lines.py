from ..utils import inch_to_base_unit, create_polygon, create_base_object
from ..coord import min_x_coord, max_x_coord, min_y_coord, max_y_coord

MINIMUM_BAY = inch_to_base_unit(12.0)
WIRE_SPACE = inch_to_base_unit(1.0)

WIRE_WIDTH = inch_to_base_unit(0.1)

# BUILDING_LAYER is a constant for the input layer name
BUILDING_LAYER = "joist"

# ANNOTATIONS_LAYER is a constant for the output layer name
ANNOTATIONS_LAYER = "annotations/joistBayLines"


class JoistBayLinesGenerator:
    def __init__(self, variation, params={}):
        self.variation = variation
        self.params = params
        self.generated_layers = self.params["layers"]
        self.changes = set()

    def generate(self):
        interior_objects = self.generated_layers[BUILDING_LAYER]["objects"]
        new_layer = self.variation.add_layer(ANNOTATIONS_LAYER)
        self.changes.add(ANNOTATIONS_LAYER)

        for i in range(len(interior_objects) - 1):
            obj = interior_objects[i]
            next_obj = interior_objects[i+1]

            min_x = max_x_coord(obj)
            max_x = min_x_coord(next_obj)
            min_y = min(min_y_coord(obj), min_y_coord(next_obj))
            max_y = max(max_y_coord(obj), max_y_coord(next_obj))

            # if bay is at least MINIMUM_BAY, create joist bay polygon
            # vertical bay
            width = max_x - min_x
            if width >= MINIMUM_BAY and width <= max_y - min_y:
                # add the wires
                curr = min_x + WIRE_SPACE
                while curr + WIRE_SPACE + WIRE_WIDTH <= max_x:
                    # render the curr wire
                    wire_coords = [
                        curr, min_y,
                        curr + WIRE_WIDTH, min_y,
                        curr + WIRE_WIDTH, max_y,
                        curr, max_y
                    ]
                    bay_line = create_polygon(wire_coords)

                    wire_base_object = create_base_object(
                        bay_line, properties={"color": "red"}
                    )
                    self.variation.add_object(
                        ANNOTATIONS_LAYER, wire_base_object)
                    curr = curr + WIRE_SPACE + WIRE_WIDTH

                # add the bay
                base_coords = [
                    min_x, min_y,
                    max_x, min_y,
                    max_x, max_y,
                    min_x, max_y,
                ]
                bay_polygon = create_polygon(base_coords)
                base_object = create_base_object(
                    bay_polygon, properties={"color": "white"}
                )
                self.variation.add_object(ANNOTATIONS_LAYER, base_object)
                continue

            min_x = min(min_x_coord(obj), min_x_coord(next_obj))
            max_x = max(max_x_coord(obj), max_x_coord(next_obj))
            min_y = max_y_coord(next_obj)
            max_y = min_y_coord(obj)

            # horizontal bay
            width = max_y - min_y
            if width >= MINIMUM_BAY and max_x - min_x > width:
                # add the wires
                curr = max_y - WIRE_SPACE

                while curr - WIRE_SPACE - WIRE_WIDTH >= min_y:
                    # render the curr wire
                    wire_coords = [
                        min_x, curr - WIRE_WIDTH,
                        max_x, curr - WIRE_WIDTH,
                        max_x, curr,
                        min_x, curr
                    ]
                    bay_line = create_polygon(wire_coords)

                    wire_base_object = create_base_object(
                        bay_line, properties={"color": "red"}
                    )
                    self.variation.add_object(
                        ANNOTATIONS_LAYER, wire_base_object)
                    curr = curr - WIRE_SPACE - WIRE_WIDTH

                # add the bay
                base_coords = [
                    min_x, min_y,
                    max_x, min_y,
                    max_x, max_y,
                    min_x, max_y,
                ]
                bay_polygon = create_polygon(base_coords)
                base_object = create_base_object(
                    bay_polygon, properties={"color": "white"}
                )
                self.variation.add_object(ANNOTATIONS_LAYER, base_object)
