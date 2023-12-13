import os
import rasterio as rio
import numpy as np
import datetime
import geopandas as gpd

from rasterio.windows import Window
from rasterio.transform import Affine
from rasterio.mask import mask
from shapely.geometry import box


def mask_name(name):
    """Retrieves name of mask file from name of AET raster.
    Parameters
    ----------
    name : str
        AET file name.
    Returns
    -------
    name_mask : str
        name of mask raster.
    """
    test = name
    doy = test[13:16]
    year = test[9:13]
    date_f = datetime.datetime(int(year), 1, 1) + datetime.timedelta(int(doy) - 1)
    date_f = date_f.date().strftime(format='%Y%m%d')
    name_mask = test[:2]+'0'+test[2]+'_'+test[3:9]+'_'+date_f+'.tif'
    return name_mask


def setting(r1, r2):
    """Retrieves different objects to process two rastes.
    Parameters
    ----------
    r1 : str
        path to raster1 (AET).
    r2 : str
        path to raster2 (mask).
    Returns
    -------
    raster1 : rasterio object
        rasterio object of raster1.
    raster2 : rasterio object
        rasterio object of raster2.
    arr_raster1 : np.array
        array of raster1 limited to intersection.
    arr_raster2 : np.array
        array of raster2 limited to intersection.
    transform : rasterio affine object
        Affine associated with intersection.
    """
    raster1 = rio.open(r1)
    raster2 = rio.open(r2)
    bb_raster1 = box(raster1.bounds[0], raster1.bounds[1], raster1.bounds[2], raster1.bounds[3])
    bb_raster2 = box(raster2.bounds[0], raster2.bounds[1], raster2.bounds[2], raster2.bounds[3])
    xminR1, yminR1, xmaxR1, ymaxR1 = raster1.bounds
    xminR2, yminR2, xmaxR2, ymaxR2 = raster2.bounds
    intersection = bb_raster1.intersection(bb_raster2)
    transform = Affine(raster1.res[0], 0.0, intersection.bounds[0], 0.0, -raster1.res[1], intersection.bounds[3])
    p1Y = intersection.bounds[3] - raster1.res[1]/2
    p1X = intersection.bounds[0] + raster1.res[0]/2
    p2Y = intersection.bounds[1] + raster1.res[1]/2
    p2X = intersection.bounds[2] - raster1.res[0]/2
    row1R1 = int((ymaxR1 - p1Y)/raster1.res[1])
    row1R2 = int((ymaxR2 - p1Y)/raster2.res[1])
    col1R1 = int((p1X - xminR1)/raster1.res[0])
    col1R2 = int((p1X - xminR2)/raster1.res[0])
    row2R1 = int((ymaxR1 - p2Y)/raster1.res[1])
    row2R2 = int((ymaxR2 - p2Y)/raster2.res[1])
    col2R1 = int((p2X - xminR1)/raster1.res[0])
    col2R2 = int((p2X - xminR2)/raster1.res[0])
    width1 = col2R1 - col1R1 + 1
    width2 = col2R2 - col1R2 + 1
    height1 = row2R1 - row1R1 + 1
    height2 = row2R2 - row1R2 + 1
    arr_raster1 = raster1.read(1, window=Window(col1R1, row1R1, width1, height1))
    arr_raster2 = raster2.read(1, window=Window(col1R2, row1R2, width2, height2))
    return raster1, raster2, arr_raster1, arr_raster2, transform


def mask_clouds(arr1, arr2):
    """Masks AET raster based on cloud and land cover mask.
    Parameters
    ----------
    arr1 : np.array
        array of raster1.
    arr2 : np.array
        array of raster2.
    Returns
    -------
    masked : np.array
        masked array.
    """
    masked = np.where(arr2 == 0, np.nan, arr1)
    return masked


def masked_array(file, LC_path):
    """Masks AET raster based on cloud and land cover mask.
    Parameters
    ----------
    file : str
        filename of raster.
    LC_path : str
        path to land cover raster.
    Returns
    -------
    mask2_lc : np.array
        array of raster masked.
    """
    cloud_mask = os.path.join('clouds', mask_name(file))
    _, _, arr1, arr2, _ = setting(file, cloud_mask)
    masked = np.where(arr2 == 0, np.nan, arr1)
    _, _, _, arr2_lc, _ = setting(cloud_mask, LC_path)
    mask1_lc = np.where((arr2_lc < 100) | (arr2_lc >310), np.nan, masked.copy())
    mask2_lc = np.where((arr2_lc > 200) & (arr2_lc < 300), np.nan, mask1_lc.copy())
    return mask2_lc  


def save_raster(raster, array, transform, out_name):
    """Saves raster as out_name.
    Parameters
    ----------
    raster : str
        filename of raster.
    array : np.array
        array associated with raster.
    transform : affine
        rasterio transform object.
    out_name : str
        name of raster to write.
    """
    with rio.open(out_name,
                  'w',
                  driver='GTiff',
                  height=array.shape[0],
                  width=array.shape[1],
                  count=1,
                  dtype=array.dtype,
                  crs=raster.crs,
                  transform=transform) as dst:
        dst.write(array, 1)
    dst.close()


def get_feature(shape_path, paddock, crs):
    """Retrieves feature from shapefile given the name of dam.
    Parameters
    ----------
    shape_path : str
        path to shapefile.
    paddock : str
        name of paddock feature.
    crs : CRS object
    Returns
    -------
    feature : shapefile.ShapeRecord
        feature associated with paddock.
    """
    shape = gpd.read_file(shape_path)
    shape['geometry'] = shape.geometry.to_crs(crs)
    feature = shape.iloc[paddock].geometry
    return feature#.values[0]


def raster_intersects(raster_path, shape_path, paddock):
    """Tests if dam intersects the raster image.
    Parameters
    ----------
    raster_path : str
        path of Sentinel 2 raster folder.
    shape_path : str
        path to shapefile.
    paddock : str
        name of paddock.
    Returns
    -------
    Boolean
        True if paddock feature intersects raster image.
    """
 
    fil = rio.open(raster_path)
    box_raster = box(*fil.bounds)
    fea = get_feature(shape_path, paddock, fil.crs)
    return box_raster.intersects(fea)


def croping(img_band, feature):
    """Crops raster based on polygon.
    Parameters
    ----------
    img_band : str
        path to img_band.
    feature : shapely Polygon
        Polygon geometry from feature.
    Returns
    -------
    out_img : np.array
        array of the image for the size of the polygon used
    out_meta : dictionary
        metadata for the cropped image
    """
    with rio.open(img_band) as src:
        out_image, out_transform = mask(src,
                                        [feature],
                                        crop=True,
                                        nodata=0)
        out_meta = src.meta
        out_meta.update({'transform':out_transform,
                         'width':out_image.shape[2],
                         'height':out_image.shape[1]})
        src.close()
    return out_image, out_meta


def get_windows(shape, paddock, img):
    """Retrieves small window from raster surrounding dam.
    Parameters
    ----------
    shape : str
        path to shapefile.
    paddock : str
        Name of dam.
    img : str
        path to img.
    Returns
    -------
    out_img : np.array
        array of the image for the size of the window used
    out_meta : dictionary
        metadata for the cropped image
    """
    raster = rio.open(img)
    fea = get_feature(shape, paddock, raster.crs)
    out_img, out_meta = croping(img, fea)
    return out_img, out_meta