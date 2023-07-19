# nisnap

![main](https://github.com/jhuguetn/nisnap/actions/workflows/main.yml/badge.svg)
[![coverage report](https://coveralls.io/repos/github/jhuguetn/nisnap/badge.svg?branch=master)](https://coveralls.io/github/xgrg/nisnap?branch=master)
[![downloads](https://img.shields.io/pypi/dm/nisnap.svg)](https://pypi.org/project/nisnap/)
[![python versions](https://img.shields.io/pypi/pyversions/nisnap.svg)](https://pypi.org/project/nisnap/)
[![pypi version](https://img.shields.io/pypi/v/nisnap.svg)](https://pypi.org/project/nisnap/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5779222.svg)](https://doi.org/10.5281/zenodo.5779222)


Create snapshots of segmentation maps produced by neuroimaging software.
Inspired by tools like [nilearn](https://nilearn.github.io/),
[visualqc](https://github.com/raamana/visualqc), [fmriprep](https://fmriprep.readthedocs.io/en/stable/) and others.

<img src="https://github.com/xgrg/nisnap/raw/master/doc/nisnap.gif" width="1000px">

<img src="https://github.com/xgrg/nisnap/raw/master/doc/nisnap2.gif" width="1000px">


## Usage

#### From a Terminal:

```sh
nisnap c1.nii.gz c2.nii.gz c3.nii.gz --bg /tmp/raw.nii.gz --opacity 50 -o /tmp/snapshot.gif

nisnap labels.nii.gz --bg raw.nii.gz --opacity 50 --axes x --contours -o /tmp/snapshot.gif
```

```sh
Arguments:

  files                 segmentation map(s) to create snapshots from

optional arguments:
  --bg BG               background image on which segmentations will be plotted.
  --axes AXES           choose the direction of the cuts (among 'x', 'y', or 'z')
  --opacity OPACITY     opacity (in %) of the segmentation maps when plotted over a background image. Only used if a background image is provided.
  --contours            if True, segmentations will be rendered as contoured regions. If False, will be rendered as superimposed masks.
  -o OUTPUT, --output OUTPUT
                        snapshot will be stored in this file. If extension is .gif, snapshot will be rendered as an animation.
  --config CONFIG       [XNAT mode] XNAT configuration file
  --nobg                [XNAT mode] no background image. Plots segmentation maps only.
  -e EXPERIMENT, --experiment EXPERIMENT
                        [XNAT mode] ID of the experiment to create snapshots from.
  --resource RESOURCE   [XNAT mode] name of the resource to download
  --cache               [XNAT mode] skip downloads (e.g. if running for a second time
  --disable_warnings
  --verbose
```


#### From IPython/Jupyter Notebook:

Example:

```python
import nisnap
filepaths = ['c1.nii.gz', 'c2.nii.gz', 'c3.nii.gz']
bg = 'source.nii.gz'
nisnap.plot_segment(filepaths, bg=bg, opacity=30, axes='x', animated=True)
```

#### Reference:

```python
def plot_segment(filepaths, axes='xyz', bg=None, opacity=30, slices=None,
        animated=False, savefig=None, contours=False, rowsize=None,
        figsize=None, width=2000):
    """Plots a set of segmentation maps/masks.

    Parameters
    ----------
    filepaths: a list of str
        Paths to segmentation maps (between 1 and 3). Must be of same dimensions
        and in same reference space.

    axes: string, or a tuple of strings
        Choose the direction of the cuts (among 'x', 'y', or 'z')

    bg: None or str
        Path to the background image that the masks will be plotted on top of.
        If nothing is specified, the segmentation maps/masks will be plotted only.
        The opacity (in %) of the segmentation maps when plotted over a background
        image. Only used if a background image is provided. Default: 10

    slices: None, or a tuple of floats
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

    contours: boolean, optional
        If True, segmentations will be rendered as contoured regions. If False,
        will be rendered as superimposed masks. Default: False

    rowsize: None, or int, or dict
        Set the number of slices per row in the final compiled figure.
        Default: {'x': 9, 'y': 9, 'z': 6}

    figsize: None, or a 2-uple of floats, or dict
        Sets the dimensions of one row of slices.
        Default: {'x': (37, 3), 'y': (40, 3), 'z': (18, 3)}

    width: int, optional
        Width (in px) of the final compiled figure. Default: 2000.


    See Also
    --------
    xnat.plot_segment : To plot segmentation maps directly providing their
        experiment_id on an XNAT instance
    """
```

### Using XNAT

#### From a Terminal:

```sh
nisnap --config .xnat.cfg -e EXPERIMENT_ID --resource ASHS --axes A --opacity 50 -o /tmp/test.gif
```

#### From IPython/Jupyter Notebook:

Example:

```python
from nisnap import xnat
xnat.plot_segment(config='/home/grg/.xnat.cfg', experiment_id='BBRC_E000',
  raw=True, opacity=30, axes='x', slices=range(100,120,2), figsize=(15,5),
  animated=True)
```

#### Reference:

```python
def plot_segment(config, experiment_id, savefig=None, slices=None,
    resource_name='SPM12_SEGMENT_T2T1_COREG',
    axes='xyz', raw=True, opacity=10, animated=False, rowsize=None,
    figsize=None, width=2000, contours=False, cache=False):
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

    slices: None, or a tuple of floats
        The indexes of the slices that will be rendered. If None is given, the
        slices are selected automatically.

    resource_name: string, optional
        Name of the resource where the segmentation maps are stored in the XNAT
        instance. Default: SPM12_SEGMENT_T2T1_COREG

    axes: string, or a tuple of strings
        Choose the direction of the cuts (among 'x', 'y', 'z')

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

    rowsize: None, or int, or dict
        Set the number of slices per row in the final compiled figure.
        Default: {'x': 9, 'y': 9, 'z': 6}

    figsize: None, or a 2-uple of floats, or dict
        Sets the dimensions of one row of slices.
        Default: {'x': (37, 3), 'y': (40, 3), 'z': (18, 3)}

    width: int, optional
        Width (in px) of the final compiled figure. Default: 2000.

    contours: boolean, optional
        If True, segmentations will be rendered as contoured regions. If False,
        will be rendered as superimposed masks. Default: False

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

## Credits

Greg Operto and Jordi Huguet ([BarcelonaBeta Brain Research Center](http://barcelonabeta.org))
