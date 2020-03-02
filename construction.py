import math
import os
import numpy as np
import matplotlib.pyplot as plt


class Component:

    def __init__(self, weight, volume, description='*unnamed*', parent=None, parent_vector=None, submerged=-1):
        """
        This represents a component connected with the platform.

        :param weight: the component's weight in [kg]
        :param volume: the component's volume in [m³]
        :param description: a short description of what the component is
        :param parent: this parameter is the component which THIS component is connected to by the parent_vector
        :param parent_vector: the position of this component in comparison with it's parent
        :param submerged: -1 (not submerged), 0 (partially submerged), 1 (fully submerged)
        """
        self.description = description
        self.weight = weight
        self.volume = volume
        self.children = []
        self.parent_vector = None
        if self.parent_vector is None:
            self.parent_vector = np.array([0, 0, 0])
        self.submerged = submerged
        if parent is not None:
            parent.assign_child(self, parent_vector)

    def assign_child(self, child, parent_vector):
        """
        Assigns a component to this component's list of children

        :param child: the component to add to the list
        :param parent_vector: the relative position of this child
        :return: None
        """
        if parent_vector is None:
            parent_vector = [0, 0, 0]
        self.children.append(child)
        child.parent_vector = np.array(parent_vector)

    def calculate_cb(self, scale, fluid_density=1000.0):
        scrap_vector, weight = self.calculate_cg()
        volume_to_displace = weight / fluid_density  # m³
        volume, partially_submerged = self.get_displaced_volume()
        volume_to_displace -= volume
        pole_volume = sum([component.volume for component in partially_submerged])
        submersion_rate = volume_to_displace / pole_volume
        s = submersion_rate * scale
        displaced_volume, vector_sum = self.get_cb(s, submersion_rate)
        cb = vector_sum / displaced_volume
        print(len(partially_submerged))
        return cb, displaced_volume, s, submersion_rate

    def get_displaced_volume(self):
        submerged_volume = 0
        partially_submerged_children = []

        for child in self.children:
            submerged_volume_child, partially_submerged_children_child = child.get_displaced_volume()
            submerged_volume += submerged_volume_child
            partially_submerged_children += partially_submerged_children_child

        if self.submerged == 1:
            submerged_volume += self.volume
        elif self.submerged == 0:
            partially_submerged_children.append(self)
        return submerged_volume, partially_submerged_children

    def calculate_cg(self):
        """
        Calculates the centre of gravity as seen by the component and it's children

        :return: A tuple containing the centre of gravity with reference to the component's position
                 and the total weight of the component and its children
        """
        weight, vector_sum = self._get_cg()
        if self.parent_vector is not None:
            vector_sum = vector_sum - self.parent_vector * weight
        return (vector_sum / weight), weight

    def get_cb(self, submersion, submersion_rate):

        offset_vector = np.array([0, 0, 0])
        displaced_volume = 0
        if self.submerged == 0:
            L = submersion/submersion_rate
            offset_vector = np.array([0, 0, -(L-submersion)/2])
            displaced_volume = self.volume * submersion_rate
        elif self.submerged == 1:
            displaced_volume = self.volume

        child_volume_sum = 0
        child_vector_sum = np.array([0, 0, 0])
        for child in self.children:
            child_volume, child_vector = child.get_cb(submersion, submersion_rate)
            child_volume_sum += child_volume
            child_vector_sum = child_vector_sum + child_vector
        self_vector_sum = self.parent_vector * (displaced_volume + child_volume_sum) + offset_vector * displaced_volume
        vector_sum = self_vector_sum + child_vector_sum
        volume_sum = child_volume_sum + displaced_volume

        return volume_sum, vector_sum

    def _get_cg(self):
        weight_sum = self.weight
        vector_sum_children = np.array([0, 0, 0])

        for child in self.children:
            child_weight, child_vector = child._get_cg()
            weight_sum += child_weight
            vector_sum_children = vector_sum_children + child_vector

        vector_sum_self = np.array([0, 0, 0])
        if self.parent_vector is not None:
            vector_sum_self = self.parent_vector * weight_sum
        vector_sum = vector_sum_children + vector_sum_self

        return weight_sum, vector_sum

    def get_tree(self, prev=''):
        """
        Retrieves a formatted string representing the ancestry of the component and its children

        :param prev: a string to be used recursively through the iterations
        :return: a string representation of the component and its children
        """
        vector = '(root)'
        if self.parent_vector is not None:
            vector = self.parent_vector.tolist()
        string = f'{prev}{self.description} {vector}\n'
        for child in self.children:
            string += child.get_tree(prev=prev + '- ')
        return string

    @staticmethod
    def calculate_submersion(m, pole_radius, volume_offset=0, height_offset=0, density=1000.0, num_pole=4):
        """
        Calculates the submersion distance of the construction. The distance is calculated as the distance the vertical
        poles must be submerged in order to support the construction's weight.
        It is assumed that the components from volume_offset are always entirely submerged.

        :param m:               the construction mass in [kg]
        :param pole_radius:     the radius of the vertical poles in [mm]
        :param volume_offset:   the total submerged volume apart from the vertical poles in [L]
        :param height_offset:   the total offset in submerged height in [mm]
        :param density:         the density of the liquid as [kg/m³]
        :param num_pole:        the number of vertical poles
        :return:                the submersion distance of the construction.
        """
        height_offset /= 1000  # convert to meter
        pole_radius /= 1000  # convert to meter
        volume_offset /= 1000  # convert from L to m³

        volume_to_displace = m / density
        volume_offset = volume_offset
        pole_cross_section = num_pole * math.pi * pole_radius ** 2
        return height_offset + (volume_to_displace - volume_offset) / pole_cross_section


def calculate_bm(r, y, displaced_volume, num_poles=4):
    pi = math.pi
    intertia = num_poles * (pi / 4 * r ** 4 + pi * r ** 2 * y ** 2)
    temp_bm = intertia / displaced_volume
    bm = np.array([0, 0, temp_bm])
    return bm