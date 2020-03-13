# nisnap

[![pipeline status](https://gitlab.com/xgrg/nisnap/badges/master/pipeline.svg)](https://gitlab.com/xgrg/nisnap/commits/master)
[![coverage report](https://gitlab.com/xgrg/nisnap/badges/master/coverage.svg)](https://gitlab.com/xgrg/nisnap/commits/master)
[![downloads](https://img.shields.io/pypi/dm/nisnap.svg)](https://pypi.org/project/nisnap/)
[![python versions](https://img.shields.io/pypi/pyversions/nisnap.svg)](https://pypi.org/project/nisnap/)
[![pypi version](https://img.shields.io/pypi/v/nisnap.svg)](https://pypi.org/project/nisnap/)


Create snapshots of segmentation maps produced by neuroimaging software.

![example](https://gitlab.com/xgrg/nisnap/raw/master/doc/nisnap.gif)

## Usage

#### From a Terminal:

```
nisnap c1.nii.gz c2.nii.gz c3.nii.gz --bg /tmp/test.nii.gz --opacity 30 -o /tmp/test.gif
```

#### From IPython/Jupyter Notebook:

Example:

```python
import nisnap
filepaths = ['c1.nii.gz', 'c2.nii.gz', 'c3.nii.gz']
bg = 'source.nii.gz'
nisnap.plot_segment(filepaths, bg=bg, opacity=30, axes='A', animated=True)
```

#### Reference:

```python
def plot_segment(filepaths, axes=('A','C','S'), bg=None, opacity=30, cut_coords=None,
        animated=False, savefig=None, figsize=None):
    """Plots a set of segmentation maps/masks.

    Parameters
    ----------
    filepaths: a list of str
        Paths to segmentation maps (between 1 and 3). Must be of same dimensions
        and in same reference space.

    axes: string, or a tuple of strings
        Choose the direction of the cuts (among 'A', 'S', 'C', 'AXIAL',
        'SAGITTAL' or 'CORONAL', or lowercase)

    bg: None or str
        Path to the background image that the masks will be plotted on top of.
        If nothing is specified, the segmentation maps/masks will be plotted only.
        The opacity (in %) of the segmentation maps when plotted over a background
        image. Only used if a background image is provided. Default: 10

    cut_coords: None, or a tuple of floats
        The indexes of the slices that will be rendered. If None is given, the
        slices are selected automatically.

    animated: boolean, optional
        If True, the snapshot will be rendered as an animated GIF.
        If False, the snapshot will be rendered as a static PNG image. Default:
        False

    savefig: string, optional
        Filepath where the resulting snapshot will be created. If None is given,
        a temporary file will be created and/or the result will be displayed
        inline in a Jupyter Notebook.

    figsize: None, or a 2-uple of floats
        Sets the figure size. Default: {'A': (37, 3), 'C': (40, 3), 'S': (18, 3)}


    See Also
    --------
    xnat.plot_segment : To plot segmentation maps directly providing their
        experiment_id on an XNAT instance
    """
```

### Using XNAT

#### From a Terminal:

```
nisnap --config /home/grg/.xnat.cfg -e BBRC_E000
```

#### From IPython/Jupyter Notebook:

Example:

```python
from nisnap import xnat
xnat.plot_segment(config='/home/grg/.xnat.cfg', experiment_id='BBRC_E000',
  raw=True, opacity=30, axes=('A'), cut_coords=range(100,120,2), animated=True)
```

#### Reference:

```python
def plot_segment(config, experiment_id, savefig=None, cut_coords=None,
    resource_name='SPM12_SEGMENT_T2T1_COREG',
    axes=('A', 'C', 'S'), raw=True, opacity=10, animated=False, figsize=None,
    cache=False):
    """Download a given experiment/resource from an XNAT instance and create
    snapshots of this resource along a selected set of slices.

    Parameters
    ----------
    config: string
        Configuration file to the XNAT instance.

    experiment_id : string
        ID of the experiment from which to download the segmentation maps and
        raw anatomical image.

    savefig: string, optional
        Filepath where the resulting snapshot will be created. If None is given,
        a temporary file will be created and/or the result will be displayed
        inline in a Jupyter Notebook.

    cut_coords: None, or a tuple of floats
        The indexes of the slices that will be rendered. If None is given, the
        slices are selected automatically.

    resource_name: string, optional
        Name of the resource where the segmentation maps are stored in the XNAT
        instance. Default: SPM12_SEGMENT_T2T1_COREG

    axes: string, or a tuple of strings
        Choose the direction of the cuts (among 'A', 'S', 'C', 'AXIAL',
        'SAGITTAL' or 'CORONAL', or lowercase)

    raw: boolean, optional
        If True, the segmentation maps will be plotted over a background image
        (e.g. anatomical T1 or T2, as in xnat.download_resources). If False,
        the segmentation maps will be rendered only. Default: True

    opacity: integer, optional
        The opacity (in %) of the segmentation maps when plotted over a background
        image. Only used if a background image is provided. Default: 10

    animated: boolean, optional
        If True, the snapshot will be rendered as an animated GIF.
        If False, the snapshot will be rendered as a static PNG image. Default:
        False

    figsize: None, or a 2-uple of floats
        Sets the figure size. Default: {'A': (37, 3), 'C': (40, 3), 'S': (18, 3)}

    bg: None or str
        Path to the background image that the masks will be plotted on top of.
        If nothing is specified, the segmentation maps/masks will be plotted only.

    cache: boolean, optional
        If False, resources will be normally downloaded from XNAT. If True,
        download will be skipped and data will be looked up locally.
        Default: False

    Notes
    -----
    Requires an XNAT instance where SPM segmentation maps will be found
    following a certain data organization in experiment resources named
    `resource_name`.

    See Also
    --------
    xnat.download_resources : To download resources (e.g. segmentation maps +
        raw images) from an XNAT instance (e.g. prior to snapshot creation)
    nisnap.plot_segment : To plot segmentation maps directly providing their
        filepaths
    """
```


```python
def download_resources(config, experiment_id, resource_name,  destination,
    raw=True, cache=False):
    """Download a given experiment/resource from an XNAT instance in a local
    destination folder.

    Parameters
    ----------
    config: string
        Configuration file to the XNAT instance.
        See http://xgrg.github.io/first-steps-with-pyxnat/ for more details.

    experiment_id : string
        ID of the experiment from which to download the segmentation maps and
        raw anatomical image.

    resource_name: string
        Name of the resource where the segmentation maps are stored in the XNAT
        instance.

    destination: string
        Destination folder where to store the downloaded resources.

    raw: boolean, optional
        If True, a raw anatomical image will be downloaded along with the
        target resources. If False, only the resources referred to by
        `resource_name` will be downloaded. Default: True

    cache: boolean, optional
        If False, resources will be normally downloaded from XNAT. If True,
        download will be skipped and data will be looked up locally.
        Default: False

    Notes
    -----
    Requires an XNAT instance where SPM segmentation maps will be found
    following a certain data organization in experiment resources named
    `resource_name`.

    See Also
    --------
    xnat.plot_segment : To plot segmentation maps directly providing their
        experiment_id on an XNAT instance
    nisnap.plot_segment : To plot segmentation maps directly providing their
        filepaths
    """

```

## How to install

```
pip install nisnap
```
