#!/usr/bin/env python2
#
##############################################################################
#
# MODULE:       landsat-8-toolkit
#
# AUTHOR(S):    Marc Becker
#
# PURPOSE:      Search and download of Landsat-8 scenes
#
# DATE:         2018-06-06
#
# COPYRIGHT:   (C) 2018 by Marc Becker, and the GRASS development team
#
#              This program is free software under the GNU General Public
#              License (>=v2). Read the file COPYING that comes with GRASS
#              for details.
##############################################################################

#%module
#% description: Search and download of Landsat-8 scenes
#% keyword: imagery
#% keyword: Landsat
#% keyword: download
#%end
#%option G_OPT_M_DIR
#% key: output
#% description: Name for output directory where to store downloaded Sentinel data
#% required: yes
#% guisection: Output
#%end
#%option
#% key: date_from
#% description: Start date ('YYYY-MM-DD')
#% answer: 2017-01-01
#% type: string
#% required: yes
#%end
#%option
#% key: date_to
#% description: End date ('YYYY-MM-DD')
#% answer: 2017-12-01
#% type: string
#% required: yes
#%end
#%option
#% key: clouds
#% type: integer
#% description: Maximum cloud cover percentage for Sentinel scene
#% answer: 30
#% required: no
#% guisection: Filter
#%end
#%option
#% key: file_key
#% description: Download files
#% multiple: no
#% options: B1,B2,B3,B4,B5,B6,B7,B8,B9,B10,B11,BQA,MTL,ANG,thumb
#% answer: thumb
#% guisection: Filter
#%end
#%option G_OPT_V_MAP
#% label: Name of input vector map to define Area of Interest (AOI)
#% description: If not given than current computational extent is used
#% required: yes
#% guisection: Region
#%end
#%flag
#% key: l
#% description: List filtered products and exist
#% guisection: Print
#%end

import sys
import os
import json

from grass.pygrass.modules import Module
from grass.script import parser, tempdir, message, error, fatal


try:
   from satsearch.search import Search, SatSearchError
except ImportError as e:
    fatal(("Module requieres satsearch library: {}".format(e)))

class LansatDownloader(object):
    def __init__(self):
        self._scenes = None

    def search(self):
        """ Search for Landsat-8 scenes """

        # Convert AOI to GeoJSON
        aoi_file = tempdir() + '/aoi_geojson.geojson'

        Module('v.out.ogr',
               overwrite=True,
               input=options['map'],
               format='GeoJSON',
               output=aoi_file)

        # Search for scenes
        with open(aoi_file) as f:
            aoi = json.dumps(json.load(f))
        search = Search(date_from=options['date_from'], date_to=options['date_to'], satellite_name='Landsat-8',
                        intersects=aoi, cloud_from=0, cloud_to=options['clouds'])
        
        self._scenes = search.scenes()
        os.remove(aoi_file)   

    def download(self):
        """ Download Landsat-8 scenes """
        
        for scene in self._scenes:
                try:
                    fname = scene.download(key=options['file_key'], path=options['output'], overwrite=True)[options['file_key']]
                    message(str(fname) + "... Done") 
                except:
                    error(str(fname) + "... Failed")

    def list(self):
        """" Create list of files """

        for scene in self._scenes:
            print("Date: {0} - Cloud: {1} - ID: {2}".format(
                scene.date,
                scene.metadata['cloud_coverage'],
                scene.scene_id
            ))
 
def main():
    downloader = LansatDownloader()
    downloader.search()
    
    if flags['l']:
        downloader.list()
        return
    else:
        downloader.download()
        return
        
    return 0

if __name__ == '__main__':
    options, flags = parser()
    sys.exit(main())

