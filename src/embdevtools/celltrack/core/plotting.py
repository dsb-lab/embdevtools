import numpy as np
from skimage.transform import resize
from matplotlib import cm

from .iters import CyclicList
from .utils_ct import printfancy


def check_and_fill_plot_args(plot_args, stack_dims):
    if "plot_layout" not in plot_args.keys():
        plot_args["plot_layout"] = (1, 1)
    if not hasattr(plot_args["plot_layout"], "__iter__"):
        printfancy("WARNING: invalid plot_layout, using (1,1) instead")
        plot_args["plot_layout"] = (1, 1)

    if "plot_overlap" not in plot_args.keys():
        plot_args["plot_overlap"] = 0
    if np.multiply(*plot_args["plot_layout"]) >= plot_args["plot_overlap"]:
        plot_args["plot_overlap"] = np.multiply(*plot_args["plot_layout"]) - 1
    if "masks_cmap" not in plot_args.keys():
        plot_args["masks_cmap"] = "tab10"
    if "plot_stack_dims" not in plot_args.keys():
        plot_args["plot_stack_dims"] = stack_dims
    if "plot_centers" not in plot_args.keys():
        plot_args["plot_centers"] = [True, True]

    plot_args["dim_change"] = plot_args["plot_stack_dims"][0] / stack_dims[-1]

    _cmap = cm.get_cmap(plot_args["masks_cmap"])
    plot_args["labels_colors"] = CyclicList(_cmap.colors)
    plot_args["plot_masks"] = True
    return plot_args


def check_stacks_for_plotting(
    stacks_for_plotting, stacks, plot_args, times, slices, xyresolution
):
    if stacks_for_plotting is None:
        stacks_for_plotting = stacks
    if len(stacks_for_plotting.shape) == 5:
        plot_args["plot_stack_dims"] = [
            plot_args["plot_stack_dims"][0],
            plot_args["plot_stack_dims"][1],
            3,
        ]

    plot_args["dim_change"] = plot_args["plot_stack_dims"][0] / stacks.shape[3]
    plot_args["_plot_xyresolution"] = xyresolution * plot_args["dim_change"]

    if plot_args["dim_change"] != 1:
        plot_stacks = np.zeros((times, slices, *plot_args["plot_stack_dims"]), dtype="uint8")
        plot_stack = np.zeros_like(plot_stacks[0,0], dtype='float16')
        for t in range(times):
            for z in range(slices):
                
                if len(plot_args["plot_stack_dims"]) == 3:
                    for ch in range(3):
                        plot_stack = resize(
                            stacks_for_plotting[t, z, :, :, ch],
                            plot_args["plot_stack_dims"][0:2],
                        )
                        norm_factor = np.max(plot_stacks[t, z, :, :, ch])
                        if norm_factor < 0.01:
                            norm_factor = 1.0
                        plot_stack[:, :, ch] = plot_stack / norm_factor
                        
                else:
                    plot_stack = resize(
                        stacks_for_plotting[t, z], plot_args["plot_stack_dims"]
                    )
                plot_stacks[t, z] = np.rint(plot_stack * 255).astype('uint8')
    else:
        plot_stacks = stacks_for_plotting

    return plot_stacks
