@echo off
REM Run in "OSGeo4W Shell" (comes with QGIS). Usage: make_tiles.bat "C:\path\RPF\A.TOC"
set TOC=%~1
gdalinfo "%TOC%" | findstr SUBDATASET_.*_NAME
set /p SDS=Paste ONE subdataset name (NITF_TOC_ENTRY:...): 
gdal_translate -of VRT -expand rgb "%SDS%" map.vrt
python -m osgeo_utils.gdal2tiles --xyz -z 7-12 --processes=4 map.vrt "%~dp0tiles"
echo Done. Run start.bat
