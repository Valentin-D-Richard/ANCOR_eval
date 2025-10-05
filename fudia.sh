#!/bin/bash

USAGE='./fudia.sh [DIR] [-o OUTPUTDIR]
Applies FUDIA to all conllu files in DIR'

DIR='.'
OUTPUTDIR='.'

# Retrieving arguments
while (( $# > 0 ))
do
    case "$1" in
        "-o"|"--output" )
            OUTPUTDIR="$2"
            shift ;;
        "-h"|"--help" )
            echo "$USAGE"
            exit ;;
        * )
            DIR="$1" ;;
    esac
    shift
done

for FILE in $DIR/*
do
    FUDIA="/home/vrichard/Documents/PhD/FUDIA/fudia.grs"
    FILENAME="${FILE##*/}"
    echo "Transforming" $FILENAME
    grew transform -grs $FUDIA  -i "$FILE" -o "$OUTPUTDIR/$FILENAME" -strat "main"
done



