# nisnap

[![pipeline status](https://gitlab.com/xgrg/nisnap/badges/master/pipeline.svg)](https://gitlab.com/xgrg/nisnap/commits/master)
[![coverage report](https://gitlab.com/xgrg/nisnap/badges/master/coverage.svg)](https://gitlab.com/xgrg/nisnap/commits/master)
[![downloads](https://img.shields.io/pypi/dm/nisnap.svg)](https://pypi.org/project/nisnap/)
[![python versions](https://img.shields.io/pypi/pyversions/nisnap.svg)](https://pypi.org/project/nisnap/)
[![pypi version](https://img.shields.io/pypi/v/nisnap.svg)](https://pypi.org/project/nisnap/)


Create snapshots of segmentation maps produced by neuroimaging software.

## Usage

From a Terminal:

```
nisnap c1.nii.gz c2.nii.gz c3.nii.gz --bg /tmp/test.nii.gz --opacity 30 -o /tmp/test.gif
```

From IPython/Jupyter Notebook:

```
import nisnap
filepaths = ['c1.nii.gz', 'c2.nii.gz', 'c3.nii.gz']
bg = 'source.nii.gz'
nisnap.plot_segment(filepaths, bg=bg, opacity=30, axes='A', animated=True)
```

### Using XNAT

From a Terminal:

```
nisnap --config /home/grg/.xnat.cfg -e BBRC_E000
```

From IPython/Jupyter Notebook:

```
from nisnap import xnat
xnat.plot_segment(config='/home/grg/.xnat.cfg', experiment_id='BBRC_E000',
  raw=True, opacity=30, axes=('A'), cut_coords=range(100,120,2), animated=True)
```


## How to install

```
pip install nisnap
```
