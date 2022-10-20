from ..utils import inch_to_base_unit, create_polygon, create_base_object
from ..coord import min_x_coord, max_x_coord, min_y_coord, max_y_coord

MINIMUM_BAY = inch_to_base_unit(12.0)

# BUILDING_LAYER is a constant for the input layer name
BUILDING_LAYER = "joist"

# ANNOTATIONS_LAYER is a constant for the output layer name
ANNOTATIONS_LAYER = "annotations/joistBay"


class JoistBayGenerator:
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
            if max_x - min_x >= MINIMUM_BAY and max_x - min_x <= max_y - min_y:
                base_coords = [
                    min_x, min_y,
                    max_x, min_y,
                    max_x, max_y,
                    min_x, max_y,
                ]
                bay_polygon = create_polygon(base_coords)
                base_object = create_base_object(
                    bay_polygon, properties={"color": "blue"}
                )
                self.variation.add_object(ANNOTATIONS_LAYER, base_object)
                continue

            min_x = min(min_x_coord(obj), min_x_coord(next_obj))
            max_x = max(max_x_coord(obj), max_x_coord(next_obj))
            min_y = max_y_coord(next_obj)
            max_y = min_y_coord(obj)

            if max_y - min_y >= MINIMUM_BAY and max_x - min_x > max_y - min_y:
                base_coords = [
                    min_x, min_y,
                    max_x, min_y,
                    max_x, max_y,
                    min_x, max_y,
                ]
                bay_polygon = create_polygon(base_coords)
                base_object = create_base_object(
                    bay_polygon, properties={"color": "blue"}
                )
                self.variation.add_object(ANNOTATIONS_LAYER, base_object)
