

# def snapshot(filepaths, fp, bg=None, axes=('A', 'C', 'S'), opacity=10):
#     import spm
#     filepaths.insert(0, bg)
#     spm.snap_files(filepaths, axes, not bg is None, opacity, fp)

def plot_segment(filepaths, bg=None, axes=('A', 'C', 'S'), opacity=30,
        animated=False, filename=None):
    fp = filename
    if filename is None:
        if animated:
            f, fp = tempfile.mkstemp(suffix='.gif')
        else:
            f, fp = tempfile.mkstemp(suffix='.jpg')
        os.close(f)


    filepaths.insert(0, bg)
    import spm
    spm.plot_segment(filepaths, axes, not bg is None, opacity=opacity,
        animated=animated, orig_fp=fp)

    if filename is None:
        from IPython.display import Image
        return Image(filename=fp.replace('.jpg', '_fusion.jpg'))
