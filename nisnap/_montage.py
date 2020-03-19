import tempfile, os
import logging as log
import shutil
from tqdm import tqdm

def __montage__(paths, paths_orig, axes, opacity, has_orig, animated,
        width=2000, savefig=None):
    from nisnap.snap import format
    f, fp = tempfile.mkstemp(suffix=format)
    os.close(f)

    montage_cmd = 'montage -resize %sx -tile 1 -background black -geometry +0+0 %s %s'%(width, '%s', '%s')
    # Compiling images into a single one (one per axis)
    for each in axes:
        cmd = montage_cmd%(' '.join(paths[each]), fp[:-4] + '_%s%s'%(each, format))
        log.debug(cmd)
        os.system(cmd)
        for e in paths[each]:
            os.unlink(e) # Delete individual snapshots

    # Create one image with the selected axes

    import os.path as op
    cmd = montage_cmd%(' '.join([fp[:-4] + '_%s%s'%(each, format) for each in axes]), fp)
    log.debug(cmd)
    os.system(cmd)
    log.debug([fp[:-4] + '_%s%s'%(each, format) for each in axes])
    log.debug([op.isfile(fp[:-4] + '_%s%s'%(each, format)) for each in axes])
    #log.info('Saved in %s'%fp)
    for each in axes:
        fp1 = fp[:-4] + '_%s%s'%(each, format)
        if op.isfile(fp1):
            os.unlink(fp1)
        else:
            from glob import glob
            log.warning('%s not found. %s'%(fp1, glob('/tmp/tmp*%s'%format)))

    if has_orig:
        # Repeat the process (montage) with the "raw" snapshots
        for each in axes:
            cmd = montage_cmd%(' '.join(paths_orig[each]), fp[:-4] + '_orig_%s%s'%(each, format))
            log.debug(cmd)
            os.system(cmd)
            for e in paths_orig[each]:
                os.unlink(e)

        # Create one image with the selected axes
        cmd = montage_cmd%(' '.join([fp[:-4] + '_orig_%s%s'%(each, format) for each in axes]),
                fp[:-4] + '_orig%s'%format)
        log.debug(cmd)
        os.system(cmd)
        #log.info('Saved in %s'%fp.replace(format, '_orig%s'%format))
        for each in axes:
            os.unlink(fp[:-4] + '_orig_%s%s'%(each, format))


    # At this point there should be two images max. (segmentation and raw image)
    composite_cmd = 'composite -dissolve %s -gravity Center %s %s -alpha Set %s'

    if has_orig:
        if animated: # will generate a .gif

            # Fading from raw data to segmentation
            l = list(range(0, opacity, int(opacity/10.0)))
            pbar = tqdm(total=2*len(l), leave=False)
            for i, opac in enumerate(l):
                cmd = composite_cmd %(opac, fp, fp[:-4] + '_orig%s'%format,
                        fp[:-4] + '_fusion_%03d%s'%(i, format))
                log.debug(cmd)
                os.system(cmd)
                pbar.update(1)

            # From segmentation to raw data
            for i, opac in enumerate(l):
                cmd = composite_cmd %(opacity - opac, fp, fp[:-4] + '_orig%s'%format,
                        fp[:-4] + '_fusion_%03d%s'%((len(l)+i), format))
                log.debug(cmd)
                os.system(cmd)
                pbar.update(1)

            pbar.update(2*len(l))
            pbar.close()

            # Collect frames and create gif
            filepaths = []
            for i, opac in enumerate(range(0, 2 * opacity, int(opacity/10.0))):
                filepaths.append(fp[:-4] + '_fusion_%03d%s'%(i, format))

            cmd = 'convert -delay 0 -loop 0 %s %s'\
                %(' '.join(filepaths), fp[:-4] + '.gif')
            log.debug(cmd)
            os.system(cmd)
            #log.info('Saved in %s'%fp.replace(format, '.gif'))

            #Removing fusions (jpeg files)
            for each in filepaths:
                os.unlink(each)
            os.unlink(fp)
            os.unlink(fp[:-4] + '_orig%s'%format)

        else:
            # Blends the two images (segmentation and original) into a composite one
            cmd = composite_cmd %(opacity, fp, fp[:-4] + '_orig%s'%format,
                    fp[:-4] + '_fusion%s'%format)
            log.debug(cmd)
            os.system(cmd)

            os.unlink(fp)
            os.unlink(fp[:-4] + '_orig%s'%format)

    # Cleaning and saving files in right location

    if has_orig:
        if animated:
            if not savefig is None:
                shutil.move(fp[:-4] + '.gif', savefig)
                log.info('Saved in %s'%savefig)

        else:
            if not savefig is None:
                shutil.move(fp[:-4] + '_fusion%s'%format, savefig)
                log.info('Saved in %s'%savefig)
            else:
                shutil.move(fp[:-4] + '_fusion%s'%format, fp)
                log.info('Saved in %s'%fp)

    else:
        if not savefig is None:
            shutil.move(fp, savefig)
            log.info('Saved in %s'%savefig)
