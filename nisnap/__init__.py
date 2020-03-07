

# def snapshot(filepaths, fp, bg=None, axes=('A', 'C', 'S'), opacity=10):
#     import spm
#     filepaths.insert(0, bg)
#     spm.snap_files(filepaths, axes, not bg is None, opacity, fp)

# def plot_segment(filepaths, bg=None, axes=('A', 'C', 'S'), opacity=30,
#         animated=False, filename=None):
#
#     from nisnap import spm
#     spm.__plot_segment__(filepaths, bg=bg, axes=axes, opacity=opacity,
#         animated=animated, filename=filename

from nisnap.spm import plot_segment
