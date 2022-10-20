from ..utils import inch_to_base_unit, create_polygon, create_base_object
from ..coord import min_x_coord, max_x_coord, min_y_coord, max_y_coord


MINIMUM_BAY = inch_to_base_unit(12.0)
WIRE_SPACE = inch_to_base_unit(1.0)

WIRE_WIDTH = inch_to_base_unit(0.1)

# BUILDING_LAYER is a constant for the input layer name
BUILDING_LAYER1 = "joistHole"
BUILDING_LAYER2 = "joist"
SUBPANEL = "subpanel"

# ANNOTATIONS_LAYER is a constant for the output layer name
ANNOTATIONS_LAYER = "annotations/subpanelNodeLines"

wires_in_subpanel_range = []


class SubpanelNodeLines:
    def __init__(self, variation, params={}):
        self.variation = variation
        self.params = params
        self.generated_layers = self.params["layers"]
        self.changes = set()

    def generate(self):
        interior_objects1 = self.generated_layers[BUILDING_LAYER1]["objects"]
        interior_objects2 = self.generated_layers[BUILDING_LAYER2]["objects"]
        subpanel = self.generated_layers[SUBPANEL]["objects"]
        mid_panel_x = 0
        wires_in_subpanel_range = []
        for x in subpanel:
            min_panel_x = min_x_coord(x)
            max_panel_x = max_x_coord(x)
            min_panel_y = min_y_coord(x)
            max_panel_y = max_y_coord(x)
            mid_panel_x = (min_panel_x + max_panel_x) / 2

        new_layer = self.variation.add_layer(ANNOTATIONS_LAYER)
        self.changes.add(ANNOTATIONS_LAYER)

        # check hole
        for obj in interior_objects1:
            min_x = min_x_coord(obj)
            max_x = max_x_coord(obj)
            min_y = min_y_coord(obj)
            max_y = max_y_coord(obj)

            # vertical hole
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
                    if mid_panel_x - WIRE_SPACE < curr < mid_panel_x + WIRE_SPACE:
                        wires_in_subpanel_range.append(wire_coords)
                    curr = curr + WIRE_SPACE + WIRE_WIDTH

            # horizontal hole
            else:
                # add the wires
                curr = max_y - WIRE_SPACE

                add_first_to_wires_subpanel = True
                add_last_to_wires_subpanel = True
                while curr - WIRE_SPACE - WIRE_WIDTH >= min_y:
                    # render the curr wire
                    wire_coords = [
                        min_x, curr - WIRE_WIDTH,
                        max_x, curr - WIRE_WIDTH,
                        max_x, curr,
                        min_x, curr
                    ]
                    # first wire of the bay to add, subpanel is above the bay
                    if min_x < mid_panel_x < max_x and min_panel_y >= curr and add_first_to_wires_subpanel:
                        add_first_to_wires_subpanel = False
                        add_last_to_wires_subpanel = False
                        wires_in_subpanel_range.append(wire_coords)

                    # last wire of the bay to add, subpanel is below the bay
                    if min_x < mid_panel_x < max_x and min_panel_y < curr and add_last_to_wires_subpanel:
                        if curr - 2*WIRE_SPACE - 2*WIRE_WIDTH < min_y:
                            wires_in_subpanel_range.append(wire_coords)
                    curr = curr - WIRE_SPACE - WIRE_WIDTH

        # joist bay
        for i in range(len(interior_objects2) - 1):
            obj = interior_objects2[i]
            next_obj = interior_objects2[i+1]

            min_x = max_x_coord(obj)
            max_x = min_x_coord(next_obj)
            min_y = min(min_y_coord(obj), min_y_coord(next_obj))
            max_y = max(max_y_coord(obj), max_y_coord(next_obj))
            # if bay is at least MINIMUM_BAY, create joist bay polygon
            # vertival bay
            width = max_x - min_x
            if width >= MINIMUM_BAY and width <= max_y - min_y:
                # add the wires
                curr = min_x + WIRE_SPACE
                while curr + WIRE_SPACE + WIRE_WIDTH <= max_x:
                    wire_coords = [
                        curr, min_y,
                        curr + WIRE_WIDTH, min_y,
                        curr + WIRE_WIDTH, max_y,
                        curr, max_y
                    ]

                    if mid_panel_x - WIRE_SPACE < curr < mid_panel_x + WIRE_SPACE:
                        wires_in_subpanel_range.append(wire_coords)
                    curr = curr + WIRE_SPACE + WIRE_WIDTH
                continue

            # horizontal hole
            min_x = min(min_x_coord(next_obj), min_x_coord(obj))
            max_x = max(max_x_coord(next_obj), max_x_coord(obj))
            min_y = max_y_coord(next_obj)
            max_y = min_y_coord(obj)

            width = max_y - min_y
            if width >= MINIMUM_BAY and max_x - min_x > width:
                # add the wires
                curr = max_y - WIRE_SPACE

                add_first_to_wires_subpanel = True
                add_last_to_wires_subpanel = True
                while curr - WIRE_SPACE - WIRE_WIDTH >= min_y:
                    wire_coords = [
                        min_x, curr - WIRE_WIDTH,
                        max_x, curr - WIRE_WIDTH,
                        max_x, curr,
                        min_x, curr
                    ]

                    # first wire of the bay to add, subpanel is above the bay
                    if min_x < mid_panel_x < max_x and min_panel_y >= curr and add_first_to_wires_subpanel:
                        add_first_to_wires_subpanel = False
                        add_last_to_wires_subpanel = False
                        wires_in_subpanel_range.append(wire_coords)

                    # last wire of the bay to add, subpanel is below the bay
                    if min_x < mid_panel_x < max_x and min_panel_y < curr and add_last_to_wires_subpanel:
                        if curr - 2*WIRE_SPACE - 2*WIRE_WIDTH < min_y:
                            wires_in_subpanel_range.append(wire_coords)
                    curr = curr - WIRE_SPACE - WIRE_WIDTH

        # now, x-values of all coords are eligible, need to find the closest y value.
        compare_panel_y = 0
        if wires_in_subpanel_range[0][1] > min_panel_y:  # wires above the panel
            compare_panel_y = max_panel_y
        else:  # wires below the panel
            compare_panel_y = min_panel_y

        x_coord = wires_in_subpanel_range[0][0]
        y_coord = wires_in_subpanel_range[0][1]
        shortest_y_to_panel = abs(
            wires_in_subpanel_range[0][1] - compare_panel_y)
        for wire in wires_in_subpanel_range:
            i = 1
            # first find the closest y to panel in the wire
            shortes_y_in_wire = abs(wire[i] - compare_panel_y)
            x_coord_temp = wire[i-1]
            y_coord_temp = wire[i]

            while i < 8:
                if abs(wire[i] - compare_panel_y) < shortes_y_in_wire:
                    shortes_y_in_wire = abs(wire[i] - compare_panel_y)
                    x_coord_temp = wire[i-1]
                    y_coord_temp = wire[i]

                i = i + 2

            if shortes_y_in_wire < shortest_y_to_panel:
                shortest_y_to_panel = shortes_y_in_wire
                x_coord = x_coord_temp
                y_coord = y_coord_temp

        wire_coords = [
            x_coord - WIRE_WIDTH,  y_coord,
            x_coord, y_coord,
            x_coord, compare_panel_y,
            x_coord - WIRE_WIDTH, compare_panel_y
        ]
        if(compare_panel_y == y_coord):  # to only make the wire noticable on the diagram
            wire_coords[1] = y_coord + 10*WIRE_WIDTH
            wire_coords[3] = y_coord + 10*WIRE_WIDTH
        elif compare_panel_y < y_coord:
            wire_coords[0] = x_coord
            wire_coords[2] = x_coord + WIRE_WIDTH
            wire_coords[4] = x_coord + WIRE_WIDTH
            wire_coords[6] = x_coord
        if abs(x_coord - mid_panel_x) > WIRE_SPACE:
            wire_coords[0] = mid_panel_x - WIRE_WIDTH
            wire_coords[2] = mid_panel_x
            wire_coords[4] = mid_panel_x
            wire_coords[6] = mid_panel_x - WIRE_WIDTH

        bay_line = create_polygon(wire_coords)

        wire_base_object = create_base_object(
            bay_line, properties={"color": "red"}
        )
        self.variation.add_object(ANNOTATIONS_LAYER, wire_base_object)
