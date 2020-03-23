import tempfile, os
import logging as log
import shutil
from tqdm import tqdm




def __vertical__(filepaths, fp):
    from PIL import Image
    images = [Image.open(x) for x in filepaths]
    widths, heights = zip(*(i.size for i in images))

    total_height = sum(heights)
    max_width = max(widths)

    new_im = Image.new('RGB', (max_width, total_height))


    y_offset = 0
    for im in images:
      x_offset = int((max_width - im.size[0])/2.0)
      new_im.paste(im, (x_offset, y_offset))
      y_offset += im.size[1]

    new_im.save(fp)

def __montage__(paths, paths_orig, axes, opacity, has_orig, animated, savefig=None):
    from nisnap.snap import format
    f, fp = tempfile.mkstemp(suffix=format)
    os.close(f)
    __vertical__([paths[each][0] for each in axes], fp)

    for each in axes:
       os.unlink(paths[each][0])

    if has_orig:
        # Create one image with the selected axes
        __vertical__([paths_orig[each][0] for each in axes], fp[:-4] + '_orig%s'%format)

        for each in axes:
           os.unlink(paths_orig[each][0])


    # At this point there should be two images max. (segmentation and raw image)
    if has_orig:
        if animated: # will generate a .gif

            # Fading from raw data to segmentation
            l = list(range(0, opacity, int(opacity/10.0)))
            pbar = tqdm(total=2*len(l), leave=False)
            for i, opac in enumerate(l):

                dissolve(fp, fp[:-4] + '_orig%s'%format, opac, fp[:-4] + '_fusion_%03d%s'%(i, format))
                pbar.update(1)

            # From segmentation to raw data
            for i, opac in enumerate(l):

                dissolve(fp, fp[:-4] + '_orig%s'%format, opacity - opac,
                    fp[:-4] + '_fusion_%03d%s'%((len(l)+i), format))
                pbar.update(1)

            pbar.update(2*len(l))
            pbar.close()

            # Collect frames and create gif
            filepaths = []
            for i, opac in enumerate(range(0, 2 * opacity, int(opacity/10.0))):
                filepaths.append(fp[:-4] + '_fusion_%03d%s'%(i, format))

            create_gif(filepaths, fp[:-4] + '.gif')

            #log.info('Saved in %s'%fp.replace(format, '.gif'))

            #Removing fusions (jpeg files)
            for each in filepaths:
                os.unlink(each)
            os.unlink(fp)
            os.unlink(fp[:-4] + '_orig%s'%format)

        else:
            # Blends the two images (segmentation and original) into a composite one

            dissolve(fp, fp[:-4] + '_orig%s'%format, opacity,
                    fp[:-4] + '_fusion%s'%format)

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

def dissolve(fp1, fp2, opacity, fp3):
    log.debug(('dissolve', fp1, fp2, opacity, fp3))
    from PIL import Image, ImageMath
    image1 = Image.open(fp1)
    image2 = Image.open(fp2)

    # Make sure images got an alpha channel
    image1 = image1.convert("RGBA")
    if image2.mode == 'I':
        image2 = ImageMath.eval('im/256', {'im':image2}).convert("RGBA")
    else:
        image2 = image2.convert("RGBA")

    # alpha-blend the images with varying values of alpha
    alphaBlended1 = Image.blend(image2, image1, alpha=opacity/100.0)
    alphaBlended1.save(fp3, "PNG")

def create_gif(filepaths, fp):
    log.debug((filepaths, fp))
    from PIL import Image
    images = [Image.open(each) for each in filepaths]
    images[0].save(fp,
        save_all=True, append_images=images[1:], optimize=False,
        duration=100, loop=0)
