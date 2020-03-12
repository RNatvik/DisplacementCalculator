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
    vertical_pipe_length = 1.01
    horizontal_pipe_length = 1.31
    vertical_pipe_volume = math.pi * pipe_radius ** 2 * vertical_pipe_length
    horizontal_pipe_volume = math.pi * pipe_radius ** 2 * horizontal_pipe_length
    ballast_density = 1025.0  # kg/m³
    additional_ballast_weight = 25

    root = Component(2.92 + 0.26 + 0.939 + 0.162, 0, description='Platform')
    electronics = Component(
        0.046 + 0.007 + 0.1 + 0.302 + 0.004 + 0.19, volume=0,
        description='electronics', parent=root, parent_vector=[0, 0, 0.05]
    )
    battery = Component(
        7.18, 0.205*0.090*0.160,
        description='battery', parent=root, parent_vector=[0, 0, -1],
        submerged=1
    )
    vertical_pipeFR = Component(

    )
    cg, weight = root.calculate_cg()
    cb, volume, submersion, submersion_rate = root.calculate_cb(vertical_pipe_length, fluid_density=1025.0)
    bm = calculate_bm(pipe_radius, platform_width / 2, volume, num_poles=6)
    data = f'Parameters:\n' \
           f'    Platform width:         {platform_width} [m]\n' \
           f'    Platform length:        {platform_length} [m]\n' \
           f'    Pipe diameter:          {pipe_diameter} [m]\n' \
           f'    Vertical pipe length:   {vertical_pipe_length} [m]\n' \
           f'    Horizontal pipe length: {horizontal_pipe_length} [m]\n' \
           f'    Ballast density:        {ballast_density} [kg/m³]\n' \
           f'    Additional ballast:     {additional_ballast_weight} [kg]\n' \
           f'Centre of gravity:   {[round(x, 5) for x in cg.tolist()]} (x, y, z)\n' \
           f'Centre of buoyancy:  {[round(x, 5) for x in cb.tolist()]} (x, y, z)\n' \
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
