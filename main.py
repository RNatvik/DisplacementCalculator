import math
import os
import matplotlib.pyplot as plt
from construction import Component, calculate_bm


def save_data(bm, cg, cb, data, title='', scrap_run=True):
    if scrap_run:
        title = 'scrap'
    os.makedirs(os.path.dirname(f'graphs/{title}/data.txt'), exist_ok=True)
    with open(f'graphs/{title}/data.txt', 'w') as file:
        file.write(data)
    x = 0
    y = 1
    z = 2
    yx = [(cb[y] + bm[y], cb[x] + bm[x]), (cg[y], cg[x]), (cb[y], cb[x])]
    xz = [(cb[x] + bm[x], cb[z] + bm[z]), (cg[x], cg[z]), (cb[x], cb[z])]
    yz = [(cb[y] + bm[y], cb[z] + bm[z]), (cg[y], cg[z]), (cb[y], cb[z])]
    figYX = plot(yx, title=title, spice='Top view', axis_label=['Y', 'X'])
    figXZ = plot(xz, title=title, spice='Side view', axis_label=['X', 'Z'])
    figYZ = plot(yz, title=title, spice='Front view', axis_label=['Y', 'Z'])

    figYX.savefig(f'graphs/{title}/figure_TopView.png')
    figXZ.savefig(f'graphs/{title}/figure_SideView.png')
    figYZ.savefig(f'graphs/{title}/figure_FrontView.png')


def plot(xy, title='', spice='', axis_label=None):
    """

    :param xy: List of tuples representing 2D coordinates
    :param title: The figure title, default empty
    :param spice: Additional figure information for title, default empty
    :param axis_label: Axis names, default x=X, y=Y
    :return:
    """
    if axis_label is None:
        axis_label = ['X', 'Y']
    fig = plt.figure()
    plt.plot(0, 0, 'o')
    for x, y in xy:
        plt.plot(x, y, 'x')
    plt.legend(['origin', 'M', 'G', 'B'])
    plt.grid()
    plt.title(f'{title} {spice}')
    plt.xlabel(axis_label[0])
    plt.ylabel(axis_label[1])
    plt.show()
    return fig


def main():

    pipe_density = 1.44  # kg/m
    platform_width = 0.7
    platform_length = 1.0
    pipe_diameter = 0.11
    pipe_radius = pipe_diameter / 2
    vertical_pipe_length = 0.7
    horizontal_pipe_length = 0  # 1.31
    vertical_pipe_volume = math.pi * pipe_radius ** 2 * vertical_pipe_length
    horizontal_pipe_volume = math.pi * pipe_radius ** 2 * horizontal_pipe_length
    ballast_density = 0.0  # kg/m³
    additional_ballast_weight = 15

    notes = f'    This is a test without horizontal pipes at the bottom of the vessel\n' \
            f'    The test is conducted with vertical pipe height compensation\n' \
            f'    as if the platform is lowered a distance down the pipes, meaning that\n' \
            f'    the vertical pipes\' total height is 1m. The height mentioned in\n' \
            f'    the parameters describe the height of pipes beneath the upper platform.'

    root = Component(2.92 + 0.26 + 0.939 + 0.162, 0, description='Platform')
    lower_platform = Component(
        3, 1 * 0.7 * 0.006, description='Lower Platform',
        parent=root, parent_vector=[0, 0, -vertical_pipe_length],
        submerged=1
    )
    electronics = Component(
        0.046 + 0.007 + 0.1 + 0.302 + 0.004 + 0.19, volume=0,
        description='electronics', parent=root, parent_vector=[0, 0, 0.05]
    )
    battery = Component(
        7.18, 0.205 * 0.090 * 0.160,
        description='battery', parent=lower_platform, parent_vector=[0, 0, 0.045],
        submerged=1
    )
    vertical_pipeFR = Component(
        pipe_density * vertical_pipe_length, vertical_pipe_volume, description='Vertical pipe, FR',
        parent=root, parent_vector=[platform_length / 2, platform_width / 2, -vertical_pipe_length / 2],
        submerged=0
    )
    vertical_pipeFL = Component(
        pipe_density * vertical_pipe_length, vertical_pipe_volume, description='Vertical pipe, FL',
        parent=root, parent_vector=[platform_length / 2, -platform_width / 2, -vertical_pipe_length / 2],
        submerged=0
    )
    vertical_pipeMR = Component(
        pipe_density * vertical_pipe_length, vertical_pipe_volume, description='Vertical pipe, MR',
        parent=root, parent_vector=[0, platform_width / 2, -vertical_pipe_length / 2],
        submerged=0
    )
    vertical_pipeML = Component(
        pipe_density * vertical_pipe_length, vertical_pipe_volume, description='Vertical pipe, ML',
        parent=root, parent_vector=[0, -platform_width / 2, -vertical_pipe_length / 2],
        submerged=0
    )
    vertical_pipeBR = Component(
        pipe_density * vertical_pipe_length, vertical_pipe_volume, description='Vertical pipe, BR',
        parent=root, parent_vector=[-platform_length / 2, platform_width / 2, -vertical_pipe_length / 2],
        submerged=0
    )
    vertical_pipeBL = Component(
        pipe_density * vertical_pipe_length, vertical_pipe_volume, description='Vertical pipe, BL',
        parent=root, parent_vector=[-platform_length / 2, -platform_width / 2, -vertical_pipe_length / 2],
        submerged=0
    )
    additional_ballast = Component(
        additional_ballast_weight, 0, description='Additional Ballast',
        parent=lower_platform, parent_vector=[0, 0, 0.1]
    )
    vertical_pipe_height_compensation = Component(
        pipe_density * (1-vertical_pipe_length) * 6, 0, description='Vertical pipe height compensation',
        parent=root, parent_vector=[0, 0, (1-vertical_pipe_length)/2]
    )

    cg, weight = root.calculate_cg()
    cb, volume, submersion, submersion_rate = root.calculate_cb(vertical_pipe_length, fluid_density=1025.0)
    bm = calculate_bm(pipe_radius, platform_width / 2, volume, num_poles=6)
    data = root.get_tree()
    data += f'\nNotes:\n{notes} \n' \
            f'Parameters:\n' \
            f'    Platform width:         {platform_width} [m]\n' \
            f'    Platform length:        {platform_length} [m]\n' \
            f'    Pipe diameter:          {pipe_diameter} [m]\n' \
            f'    Vertical pipe length:   {vertical_pipe_length} [m]\n' \
            f'    Horizontal pipe length: {horizontal_pipe_length} [m]\n' \
            f'    Ballast density:        {ballast_density} [kg/m³]\n' \
            f'    Additional ballast:     {additional_ballast_weight} [kg]\n' \
            f'Centre of gravity:   {[round(x, 5) for x in cg.tolist()]} (x, y, z)\n' \
            f'Centre of buoyancy:  {[round(x, 5) for x in cb.tolist()]} (x, y, z)\n' \
            f'BM vector:           {[round(x, 5) for x in bm.tolist()]} (x, y, z)\n' \
            f'Total weight:        {weight} [kg]\n' \
            f'Submerged volume:    {volume} [m³]\n' \
            f'Submersion / rate:   {submersion} [m] / {submersion_rate} [ratio]'
    save_data(
        bm, cg, cb, data,
        title=f'110mm_6p_070x100_{additional_ballast_weight}_additional_ballast_height_compensated',
        scrap_run=True
    )
    print(data)


if __name__ == '__main__':
    main()
