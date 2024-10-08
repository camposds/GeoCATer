#!/bin/bash

QGIS_PREFIX_PATH=/usr
if [ -n "$1" ]; then
    QGIS_PREFIX_PATH=$1
fi

#echo ${QGIS_PREFIX_PATH}


export QGIS_PREFIX_PATH=${QGIS_PREFIX_PATH}
export QGIS_PATH=${QGIS_PREFIX_PATH}
export LD_LIBRARY_PATH=${QGIS_PREFIX_PATH}/lib/grass82/lib
export PYTHONPATH=usr/share/qgis/python:usr/share/qgis/python/plugins

#echo "QGIS PATH: $QGIS_PREFIX_PATH"
export QGIS_DEBUG=0
export QGIS_LOG_FILE=/tmp/inasafe/realtime/logs/qgis.log

export PATH=${QGIS_PREFIX_PATH}/local/bin:${QGIS_PREFIX_PATH}/bin:/bin:${QGIS_PREFIX_PATH}/local/games:${QGIS_PREFIX_PATH}/games

#echo "This script is intended to be sourced to set up your shell to"
#echo "use a QGIS 3.0 built in $QGIS_PREFIX_PATH"
#echo
#echo "To use it do:"
#echo "source $BASH_SOURCE /your/optional/install/path"
#echo
#echo "Then use the make file supplied here e.g. make guitest"
