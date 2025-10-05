#! /usr/bin/env python3

import os
import sys
# import xml.etree.ElementTree as ET
from lxml import etree

ns = {'tei': 'http://www.tei-c.org/ns/1.0',
      'xml': 'http://www.w3.org/XML/1998/namespace'} # tei and xml prefixes
int_words = ['qui', 'oU', 'quoi', 'quand', 'comment', 'pourquoi',
             'quel', 'quelle', 'quelles', 'quels', 'combien']
# Main French QU-words ('lequel' and composites are omitted)
# Diacritics were removed from the corpus, and 'ù' was changed to 'U'


##### Arguments

USAGE = """./export_text.py DIR
Exports all the .xml glozz-output files in DIR to a text format"""

DIR = "." # default execution in the current directory
OUTPUTDIR = "."

if len(sys.argv) > 2:
    print("Error, too many arguments or missing directory.", file=sys.stderr)
    print(USAGE, file=sys.stderr)
    exit(2)
if len(sys.argv) == 2:
    DIR = sys.argv[1]
    os.chdir(DIR)


##### Utils

def attrib(tree, prefix:str, tag:str) -> str:
    """Returns the attribute of the root of tree of name prefix:tag,
    given the ns dictionary"""
    try:
        return tree.attrib['{'+ns[prefix]+'}'+tag]
    except KeyError:
        return ""
    

##### Main function

def textify(filename:str):
    """Input: name of a TEI corpus document
    Output: sentences containing coreferring phrases,
        which first one is a QU-word"""
    # Parsing the file
    # try:
    tree = etree.parse(filename)
    # except ET.ParseError as err:
    #     print("File:", filename, file=sys.stderr)
    #     print(err, file=sys.stderr)
    #     exit(1)
    root = tree.getroot()

    # Getting all turns
    turns = root.findall(".//tei:u",ns)

    # Opening file and writing
    file_id = '.'.join(filename.split('.')[:-1])
    with open(file_id + ".conllu", 'w') as o_file:
        o_file.write("# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC\n")
        for (j,turn) in enumerate(turns):
            ws = turn.findall(".//tei:w",ns)

            # Formatting the turn into a conllu sentence
            chunks = etree.tostring(turn, encoding='unicode', method='text').split('\n')
            string = ' '.join([chunk.strip() for chunk in chunks if chunk.strip() != ""])
            if len(ws) >= 0:
                o_file.write("# sent_id = " + file_id + '_' + str(j) + '\n')
                o_file.write("# text = " + string + '\n')
                # Writing a token per line
                for (i,w) in enumerate(ws):
                    line = str(i+1) + '\t' + w.text + (7 * '\t_') + '\t' + "id=" + attrib(w,'xml','id')
                    o_file.write(line + '\n')

                o_file.write('\n')



##### Main loop
        
for filename in os.listdir('.'):
    if filename[-4:] == ".tei":
        try:
            textify(filename)
        except KeyError as err:
            print("Warning: KeyError", err, "at file:",
                  filename, file=sys.stderr)


