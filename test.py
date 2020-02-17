import math

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


def plot(bm, cg, cb):
    plt.figure()
    plt.plot(0, 0, 'x')
    plt.plot(0, cb[2] + bm[2], 'x')
    plt.plot(0, cg[2], 'x')
    plt.plot(0, cb[2], 'x')
    plt.legend(['origin', 'm', 'cg', 'cb'])
    plt.xlim([-0.1, 0.1])
    plt.ylim([-1.1, 0.1])
    plt.grid()
    plt.show()


def main():
    platform_width = 1
    platform_length = 1
    pipe_diameter = 0.11
    pipe_radius = pipe_diameter / 2
    vertical_pipe_length = 1
    horizontal_pipe_length = 1
    vertical_pipe_volume = math.pi * pipe_radius ** 2 * vertical_pipe_length
    horizontal_pipe_volume = math.pi * pipe_radius ** 2 * horizontal_pipe_length
    ballast_density = 1025.0  # kg/m³

    root = Component(4.3, 0, description='Platform')
    electronics = Component(
        7.18 + 0.046 + 0.007 + 0.1 + 0.302 + 0.004 + 0.19, volume=0,
        description='electronics', parent=root, parent_vector=[0, 0, 0.05]
    )
    pipeFL = Component(
        1.44 * vertical_pipe_length, vertical_pipe_volume,
        description='FL pipe',
        parent=root, parent_vector=[platform_length / 2, -platform_width / 2, -vertical_pipe_length / 2],
        submerged=0
    )
    pipeFR = Component(
        1.44 * vertical_pipe_length, vertical_pipe_volume,
        description='FR pipe',
        parent=root, parent_vector=[platform_length / 2, platform_width / 2, -vertical_pipe_length / 2],
        submerged=0
    )
    pipeBL = Component(
        1.44 * vertical_pipe_length, vertical_pipe_volume,
        description='BL pipe',
        parent=root, parent_vector=[-platform_length / 2, -platform_width / 2, -vertical_pipe_length / 2],
        submerged=0
    )
    pipeBR = Component(
        1.44 * vertical_pipe_length, vertical_pipe_volume,
        description='BR pipe',
        parent=root, parent_vector=[-platform_length / 2, platform_width / 2, -vertical_pipe_length / 2],
        submerged=0
    )
    ballast_pipeR = Component(
        1.44 * horizontal_pipe_length, horizontal_pipe_volume,
        description='Right ballast pipe',
        parent=pipeFR, parent_vector=[-horizontal_pipe_length / 2, 0, -vertical_pipe_length / 2],
        submerged=1
    )
    ballast_pipeL = Component(
        1.44 * horizontal_pipe_length, horizontal_pipe_volume,
        description='Left ballast pipe',
        parent=pipeFL, parent_vector=[-horizontal_pipe_length / 2, 0, -vertical_pipe_length / 2],
        submerged=1
    )
    ballast1 = Component(
        ballast_density * horizontal_pipe_volume, 0,
        description='Ballast in left ballast pipe',
        parent=ballast_pipeL
    )
    ballast2 = Component(
        ballast_density * horizontal_pipe_volume, 0,
        description='Ballast in right ballast pipe',
        parent=ballast_pipeR
    )
    motorFL = Component(
        1.3, 0.0005,
        description='Front left motor',
        parent=pipeFL, parent_vector=[0, 0, -(vertical_pipe_length / 2 + pipe_diameter)],
        submerged=1
    )
    motorFR = Component(
        1.3, 0.0005,
        description='Front right motor',
        parent=pipeFR, parent_vector=[0, 0, -(vertical_pipe_length / 2 + pipe_diameter)],
        submerged=1
    )
    motorBL = Component(
        1.3, 0.0005,
        description='Back left motor',
        parent=pipeBL, parent_vector=[0, 0, -(vertical_pipe_length / 2 + pipe_diameter)],
        submerged=1
    )
    motorBR = Component(
        1.3, 0.0005,
        description='Back right motor',
        parent=pipeBR, parent_vector=[0, 0, -(vertical_pipe_length / 2 + pipe_diameter)],
        submerged=1
    )
    additional_ballast = Component(
        5, 0,
        description='additional ballast',
        parent=root, parent_vector=[0, 0, -vertical_pipe_length]
    )
    # pipeML = Component(
    #     1.44 * vertical_pipe_length, vertical_pipe_volume,
    #     description='pipeML',
    #     parent=root, parent_vector=[0, -platform_width / 2, -vertical_pipe_length / 2],
    #     submerged=0
    # )
    # pipeMR = Component(
    #     1.44 * vertical_pipe_length, vertical_pipe_volume,
    #     description='pipeMR',
    #     parent=root, parent_vector=[0, platform_width / 2, -vertical_pipe_length / 2],
    #     submerged=0
    # )


    cg, weight = root.calculate_cg()
    cb, volume, submersion, submersion_rate = root.calculate_cb(vertical_pipe_length, fluid_density=1025.0)
    bm = calculate_bm(pipe_radius, platform_width / 2, volume, num_poles=4)
    plot(bm, cg, cb)
    # print(root.get_tree())
    print(f'Centre of gravity:   {cg}\n'
          f'Centre of buoyancy:  {cb}\n'
          f'Construction weight: {weight}\n'
          f'Submerged volume:    {volume}\n'
          f'Submersion / rate:   {submersion} / {submersion_rate}'
          )


if __name__ == '__main__':
    main()
