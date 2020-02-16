import numpy as np

HORIZONTAL_PIPE_WEIGHT = 10  # kg
VERTICAL_PIPE_WEIGHT = 0.5
PLATFORM_WEIGHT = 12
TOTAL_WEIGHT = HORIZONTAL_PIPE_WEIGHT*2 + VERTICAL_PIPE_WEIGHT*4 + PLATFORM_WEIGHT


# x, y, z
cg_hp1 = np.array([0, -0.25, -1.0])*HORIZONTAL_PIPE_WEIGHT
cg_hp2 = np.array([0, 0.25, -1.0])*HORIZONTAL_PIPE_WEIGHT
cg_vp1 = np.array([0.4, -0.25, -0.5])*VERTICAL_PIPE_WEIGHT
cg_vp2 = np.array([0.4, 0.25, -0.5])*VERTICAL_PIPE_WEIGHT
cg_vp3 = np.array([-0.4, 0.25, -0.5])*VERTICAL_PIPE_WEIGHT
cg_vp4 = np.array([-0.4, -0.25, -0.5])*VERTICAL_PIPE_WEIGHT
cg_p = np.array([0, 0, 0])*PLATFORM_WEIGHT

cg = (cg_hp1 + cg_hp2 + cg_vp1 + cg_vp2 + cg_vp3 + cg_vp4 + cg_p) / TOTAL_WEIGHT
print(cg)
