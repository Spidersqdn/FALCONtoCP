@echo off
REM Run in "OSGeo4W Shell" (QGIS). Usage: make_pmtiles.bat "C:\path\RPF\A.TOC"
REM Needs pmtiles.exe (github.com/protomaps/go-pmtiles/releases) in this folder
set TOC=%~1
gdalinfo "%TOC%" | findstr SUBDATASET_.*_NAME
set /p SDS=Paste ONE subdataset name (NITF_TOC_ENTRY:...): 
gdal_translate -of VRT -expand rgb "%SDS%" map.vrt || gdal_translate -of VRT "%SDS%" map.vrt
gdal_translate -of MBTILES -co TILE_FORMAT=JPEG -co QUALITY=80 map.vrt map.mbtiles
gdaladdo -r average map.mbtiles 2 4 8 16 32
"%~dp0pmtiles.exe" convert map.mbtiles "%~dp0map.pmtiles"
echo Done: map.pmtiles
