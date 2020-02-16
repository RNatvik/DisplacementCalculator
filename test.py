import math

import numpy as np


class Component:

    def __init__(self, weight, volume, description='*unnamed*', parent=None, parent_vector=None):
        """
        This represents a component connected with the platform.

        :param weight: the component's weight in [kg]
        :param volume: the component's volume in [L]
        :param description: a short description of what the component is
        :param parent: this parameter is the component which THIS component is connected to by the parent_vector
        :param parent_vector: the position of this component in comparison with it's parent
        """
        self.description = description
        self.weight = weight
        self.volume = volume
        self.children = []
        self.parent_vector = None
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

    def calculate_cg(self):
        """
        Calculates the centre of gravity as seen by the component and it's children

        :return: A tuple containing the centre of gravity with reference to the component's position
                 and the total weight of the component and its children
        """
        weight, vector_sum = self._get_cg()
        if self.parent_vector is not None:
            vector_sum = vector_sum - self.parent_vector * weight
        return (vector_sum / weight).tolist(), weight

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


if __name__ == '__main__':
    d = 110  # Diameter in mm
    d /= 1000  # convert to meter
    L = 1  # length in m
    v_pipe = (math.pi * (d / 2) ** 2 * L) * 1000
    root = Component(12, 0, 'Platform')
    pole1 = Component(0.5, v_pipe, parent=root, parent_vector=[0.4, -0.25, -0.5], description='Vertical pole front left')
    pole2 = Component(0.5, v_pipe, parent=root, parent_vector=[0.4, 0.25, -0.5], description='Vertical pole front right')
    pole3 = Component(0.5, v_pipe, parent=root, parent_vector=[-0.4, 0.25, -0.5], description='Vertical pole back left')
    pole4 = Component(0.5, v_pipe, parent=root, parent_vector=[-0.4, -0.25, -0.5], description='Vertical pole back right')
    beam1 = Component(0.5, v_pipe, parent=root, parent_vector=[0, -0.25, -1], description='Horizontal beam left')
    beam2 = Component(0.5, v_pipe, parent=root, parent_vector=[0, 0.25, -1], description='Horizontal beam right')
    ballast1 = Component(10, 0, parent=beam1, description='Left beam ballast')
    ballast2 = Component(10, 0, parent=beam2, description='Right beam ballast')
    motor1 = Component(1.3, 0, parent=beam1, parent_vector=[0.4, 0, 0], description='Front Left motor')
    motor2 = Component(1.3, 0, parent=beam2, parent_vector=[0.4, 0, 0], description='Front Right motor')
    motor3 = Component(1.3, 0, parent=beam1, parent_vector=[-0.4, 0, 0], description='Back Left motor')
    motor4 = Component(1.3, 0, parent=beam2, parent_vector=[-0.4, 0, 0], description='Back Right motor')

    cg, weight = root.calculate_cg()
    tree = root.get_tree()
    submerged_volume = beam1.volume + beam2.volume
    submersion = calculate_submersion(weight, 55, volume_offset=submerged_volume, height_offset=0)
    print(f'{tree}\n'
          f'Centre of mass, as seen from root: {cg} (in [m])\n'
          f'Total weight of root and children: {weight} [kg]\n'
          f'Submersion of vertical pipes:      {submersion} [m]')