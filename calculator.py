import math


def main(lower_pipe_diameter, pole_diameter, lower_length, height, num_lower=2, num_pole=4, submersion_rate=2/3, ballast_weight_pr_litre=1.0):
    """
    Calculates metrics for displacement of cylinders underwater. The cylinders are assumed to be weightless
    :param pipe_diameter: pipe diameter in mm
    :param lower_length: length of horizontal pipes in m
    :param height: length of vertical pipes in m
    :param num_lower: number of horizontal pipes
    :param num_pole: number of vertical pipes
    :param submersion_rate: how much of the vessel is desired submerged
    :param ballast_weight_pr_litre: density of ballast to be used in horizontal cylinders
    :return:
    """
    rl = (lower_pipe_diameter/1000)/2
    rp = (pole_diameter/1000)/2
    v_lower = math.pi * (rl**2) * lower_length * 1000  # *1000 to convert to litre
    v_pole = math.pi * (rp**2) * height * 1000

    vt_lower = num_lower * v_lower
    vt_pole = num_pole * v_pole

    vt = vt_lower + vt_pole

    v_submerged = vt_lower + vt_pole*submersion_rate

    ballast_weight = vt_lower*ballast_weight_pr_litre

    net_positive = vt - ballast_weight
    partial_positive = v_submerged - ballast_weight

    print(f'Parameters:\n'
          f'    Lower Pipe diameter: {lower_pipe_diameter}mm\n'
          f'    Pole diameter:       {pole_diameter}mm\n'
          f'    Horizontal length:   {lower_length}m\n'
          f'    Vertical length:     {height}m\n'
          f'    Num horizontal:      {num_lower}\n'
          f'    Num vertical:        {num_pole}\n'
          f'    Submersion rate:     {submersion_rate}\n'
          f'    Ballast weight:      {ballast_weight_pr_litre} kg/L\n'
          f'\n'
          f'Volume of each horizontal pipe:     {round(v_lower, 2)} L\n'
          f'Volume of each vertical pipe:       {round(v_pole, 2)} L\n'
          f'Total volume of horizontal pipes:   {round(vt_lower, 2)} L\n'
          f'Total volume of vertical pipes:     {round(vt_pole, 2)} L\n'
          f'Total volume of all pipes:          {round(vt, 2)} L\n'
          f'\n'
          f'Desired submerged volume:           {round(v_submerged, 2)} L\n'
          f'Ballast weight:                     {round(ballast_weight, 2)} kg\n'
          f'Fully submerged net positive:       {round(net_positive, 2)} kg\n'
          f'Partially submerged net positive:   {round(partial_positive, 2)} kg \n')


if __name__ == '__main__':
    print('------------ 110/110, 4-pole---------------')
    main(110, 110, 1, 1, num_pole=4, ballast_weight_pr_litre=1)
    print('------------ 110/75, 4-pole---------------')
    main(110, 75, 1, 1, num_pole=4, ballast_weight_pr_litre=1)
    print('------------ 110/75, 6-pole---------------')
    main(110, 75, 1, 1, num_pole=6, ballast_weight_pr_litre=1, submersion_rate=0.82)
    construction_weight = 12

    battery_weight = 7.5
    motor_weight = 1.3*4
    offset_weight = 2
    print('Weight:', sum([construction_weight, battery_weight, motor_weight, offset_weight]))

    dy = 0.050
    h = 2
    m = 0.650
    ry = dy/2
    ri = ry - 0.002
    vy = math.pi * ry**2 * h
    vi = math.pi * ri**2 * h
    v = vy-vi
    density = m/v
    print(density)

    dy = 0.05
    h = 1
    ry = dy/2
    ri = ry - 0.002
    vy = math.pi * ry ** 2 * h
    vi = math.pi * ri ** 2 * h
    v = vy - vi
    m = v * density
    print(m)