from ..utils import inch_to_base_unit, create_polygon, create_base_object, create_line
from ..coord import min_x_coord, max_x_coord, min_y_coord, max_y_coord

WIRE_SPACE = inch_to_base_unit(1.0)

WIRE_WIDTH = inch_to_base_unit(0.1)

# BUILDING_LAYER is a constant for the input layer name
BUILDING_LAYER = "joistHole"

# ANNOTATIONS_LAYER is a constant for the output layer name
ANNOTATIONS_LAYER = "annotations/joistHoleLines"


class JoistHoleLinesGenerator:
    def __init__(self, variation, params={}):
        self.variation = variation
        self.params = params
        self.generated_layers = self.params["layers"]
        self.changes = set()

    def generate(self):
        interior_objects = self.generated_layers[BUILDING_LAYER]["objects"]

        new_layer = self.variation.add_layer(ANNOTATIONS_LAYER)
        self.changes.add(ANNOTATIONS_LAYER)

        for obj in interior_objects:
            min_x = min_x_coord(obj)
            max_x = max_x_coord(obj)
            min_y = min_y_coord(obj)
            max_y = max_y_coord(obj)

            if max_x - min_x <= max_y - min_y:
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
            else:
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
