"""
This is an example Base generator class. This generator will offset the
building polygon(s) outward by 3 inches and save these new polygons
to a new annotations base layer.
"""
from ..utils import inch_to_base_unit, create_polygon, create_base_object

# OFFSET_DISTANCE is a constant that is used by the base generator class.
# The offset distance is specified in inches because that is easier
# to work with in-code than base units. The helper function "inch_to_base_unit"
# can be used to convert to base units and keep the generator unit-agnostic.
OFFSET_DISTANCE = inch_to_base_unit(6.0)  # inches

# BUILDING_LAYER is a constant for the input layer name
BUILDING_LAYER = "building"

# ANNOTATIONS_LAYER is a constant for the output layer name
ANNOTATIONS_LAYER = "annotations/buildingOffset"


class BuildingOffsetGenerator:
    def __init__(self, variation, params={}):
        # Make the variation globally accessible by all methods in this class.
        self.variation = variation

        # Generators can accept arbitrary parameters, make the parameters
        # globally accessible by all methods in this class.
        self.params = params

        # Generators can access all existing base layers here too. This
        # is useful to access generated base layers as opposed to test
        # data input layers.
        self.generated_layers = self.params["layers"]

        # Create a set to track the base layers that change by this generator.
        # This is used later by a parent routine so we know which base layers
        # to return.
        self.changes = set()

    def generate(self):
        # Get the objects on the design interior layer, we'll use these to
        # create our new offset geometry.
        interior_objects = self.variation.layers[BUILDING_LAYER]["objects"]

        # Create the new layer object in the variation and add the changes
        # to the generator.changes set to keep track
        new_layer = self.variation.add_layer(ANNOTATIONS_LAYER)
        self.changes.add(ANNOTATIONS_LAYER)

        # Loop through each interior object
        for obj in interior_objects:
            # Create a shapely object for each base geometry
            interior_polygon = create_polygon(obj["base"]["polygon"])
            # Use shapely to offset the geometry outward
            offset_polygon = interior_polygon.buffer(
                OFFSET_DISTANCE, join_style=2)
            # Turn the shapely geometry back into a base object
            base_object = create_base_object(
                offset_polygon, properties={"color": "red"}
            )
            # Add the base object to the variation
            self.variation.add_object(ANNOTATIONS_LAYER, base_object)
