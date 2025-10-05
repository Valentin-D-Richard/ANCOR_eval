#! /usr/bin/env python3

import os
import sys
from lxml import etree

ns = {'tei': 'http://www.tei-c.org/ns/1.0',
      'xml': 'http://www.w3.org/XML/1998/namespace'} # tei and xml prefixes
int_words = ['qui', 'où', 'quoi', 'quand', 'comment', 'pourquoi',
             'quel', 'quelle', 'quelles', 'quels', 'combien', 'que', "qu'",
             'lequel', 'lesquels', 'laquelle', 'lesquelles']
# Main French QU-words ('lequel' and composites are omitted)
# Diacritics were removed from the corpus, and 'ù' was changed to 'U'

USAGE = """./extract1.py [DIR] [--newoff --incass --prooff]
Prints a list of the anaphoric chain of the tei files in DIR
in a markdown format
DIR     default is '.'
--newoff    Selects NEW=YES as well as the other mentions
--incass    Filters in associative (aka. bridging) chains
--prooff    Selects chains with at least one pronoun and the other ones"""
DIR = "."
NEW = True
COREF = True
PRO = True

# Retrieving arguments
for arg in sys.argv[1:]:
    match arg:
        case "-h" | "--help":
            print(USAGE)
            exit()
        case "--newoff":
            NEW = False
        case "--incass":
            COREF = False
        case "--prooff":
            PRO = False
        case _:
            DIR = arg


##### Utils

def attrib(tree, prefix:str, tag:str) -> str:
    """Returns the attribute of the root of tree of name prefix:tag,
    given the ns dictionary"""
    try:
        return tree.attrib['{'+ns[prefix]+'}'+tag]
    except KeyError:
        return ""
    
def boolify(s:str):
    return s == "YES"

def word_id(id:str):
    """Returns the integer section, utterance and word ids
    of a word id given as a string"""
    s = id.split('.')
    return (int(s[0].strip('s')), int(s[1].strip('u')), int(s[2].strip('w')))

def string_id(s:int, u:int, w:int):
    """Returns the string id of section s, utterance u and word w"""
    return "s"+str(s)+".u"+str(u)+".w"+str(w)

def ids_in_between(from_id:str, to_id:str):
    """Returns the list of str ids in between (largely) from_id and to_id
    We assume that both are in the same section and utterrance"""
    from_id = word_id(from_id)
    to_id = word_id(to_id)
    assert from_id[0] == to_id[0] and from_id[1] == to_id[1]
    return [string_id(to_id[0],to_id[1],i) for i in range(from_id[2], to_id[2]+1)]


##### Main function

def search_int_coref(filename:str):
    """Input: name of a TEI corpus document
    Output: sentences containing coreferring phrases,
        which first one is a QU-word"""
    # Parsing the file
    try:
        tree = etree.parse(filename)
    except etree.ParseError as err:
        print("File:", filename, file=sys.stderr)
        print(err, file=sys.stderr)
        exit(1)
    root = tree.getroot()

    # Retrieving subtrees
    sent_trees = []
    for t in root[1][0].findall('tei:div', ns):
        if attrib(t, 'tei', 'type') == "section":
            sent_trees += t.findall('tei:u', ns)
    ment_trees = []
    for t in root[2].findall('tei:spanGrp', ns):
        ment_trees += t.findall('tei:span', ns)
    coref_trees = []
    for t in root[2].findall('tei:linkGrp', ns):
        coref_trees += t.findall('tei:link', ns)

    ### Formatting word ids, mentions and coreferences
    # Words and sentences
    words = []
    for s in sent_trees:
        words.append([])
        for w in s.findall('tei:w', ns):
            words[-1].append([attrib(w,'xml','id'), w.text])
        for pc in s.findall('tei:pc', ns):
            words[-1].append([attrib(pc,'xml','id'), pc.text])
        words[-1].sort(key=lambda w_i: word_id(w_i[0]))
    id2words = {w[0]:w[1] for s in words for w in s}
    id2sents = {w[0]:i for i,s in enumerate(words) for w in s}

    # Mentions
    mentions = []
    for m in ment_trees:
        target = attrib(m,'tei','target').replace('#','')
        if len(target) > 0: # Discontinuous mentions
            mentions.append([attrib(m,'xml','id')] + target.split(' '))
        else: # Continuous mentions
            target = ids_in_between(attrib(m,'tei','from').strip('#'), attrib(m,'tei','to').strip('#'))
            mentions.append([attrib(m,'xml','id')] + target)
    mention2ids = {m[0]:m[1:] for m in mentions}
    for m in mention2ids.keys():
        mention2ids[m].sort(key=lambda id: word_id(id))

    # Mention novelty feature
    mention2novelty = {}
    mention2pron = {}
    for t in root[2].findall('tei:div', ns):
        if attrib(t,'tei','type') == "unit-fs":
            for subt in t.findall('tei:fs', ns):
                m = '-'.join(attrib(subt, 'xml', 'id').split('-')[:-1])
                for f in subt.findall('tei:f', ns):
                    if attrib(f, 'tei', 'name') == "NEW":
                        mention2novelty[m] = boolify(f[0].text)
                    if attrib(f, 'tei', 'name') == "type":
                        mention2pron[m] = f[0].text == "PR"

    # Coreferences
    corefs = [[attrib(c,'xml','id')] \
          + attrib(c,'tei','target').replace('#','').split(' ')
            for c in coref_trees]
    coref2mentions = {
        c[0]:[m for m in c[1:] if m in mention2ids.keys()] for c in corefs}
    temp_corefs = list(coref2mentions.keys())
    for c in temp_corefs:
        if len(coref2mentions[c]) < 2: # Removing coreferences with only one mention
            del coref2mentions[c]
        else:
            coref2mentions[c].sort(key=lambda m: word_id(mention2ids[m][0]))

    # Filtering to interrogative mentions and coreferences
    #  and mentions introducing a NEW discourse referent, if NEW
    int_mentions = []
    for m in mention2ids.keys():
        for id in mention2ids[m]:
            if id2words[id] == "importe": # Ignoring "n'importe + QU" phrases
                break
            if id2words[id] in int_words:
                if m not in mention2novelty.keys():
                    raise KeyError("Mention",m,"not detected in FS description divisions.")
                if not NEW or (m in mention2novelty.keys() and mention2novelty[m]):
                    int_mentions.append(m)

    # Filtering out associative chains
    int_corefs = []
    for c in coref2mentions.keys():
        exists_pron = False
        if not COREF or c[:13] != "r-ASSOCIATIVE": # Removing associative coindexation, if COREF
            for m in coref2mentions[c]:
                if mention2pron[m]:
                    exists_pron = True
                if m in int_mentions:
                    int_corefs.append(c)
            if PRO and not exists_pron and c in int_corefs: 
                int_corefs.remove(c) # Removing chains with no pronominal reference

    # Removing corefs which are included in other ones
    temp_int_corefs = list(int_corefs)
    for c2 in temp_int_corefs:
        for c1 in temp_int_corefs:
            if set(coref2mentions[c2]).issubset(set(coref2mentions[c1])) \
                    and c1 != c2 and c2 in int_corefs and c1 in int_corefs:
                int_corefs.remove(c2)

    # Formatting output
    output = []
    for c in int_corefs:
        ellipsis = False
        string = ""
        cur_ment_idx = -1 # Mentions are supposed to be sorted

        ment_sents = set([id2sents[mention2ids[m][0]] for m in coref2mentions[c]])
        for ment_sent in range(min(ment_sents), max(ment_sents)+1):

            if not ment_sent-1 in ment_sents and not ment_sent in ment_sents \
                and not ment_sent+1 in ment_sents:
                if not ellipsis:
                    ellipsis = True
                    string += " [...]"

            else:
                ellipsis = False
                for id_word in words[ment_sent]:
                    string += " "
                    if cur_ment_idx+1 < len(coref2mentions[c]) and \
                        id_word[0] == mention2ids[coref2mentions[c][cur_ment_idx+1]][0]:
                        cur_ment_idx += 1
                        string += "**["
                    string += id_word[1]
                    if id_word[0] == mention2ids[coref2mentions[c][cur_ment_idx]][-1]:
                        string += "]**"
                string += "."
        output.append([c, coref2mentions[c], string[1:]])

    return output


##### Main loop
        
for filename in os.listdir(DIR):
    if filename[-4:] == ".tei":
        try:
            output = search_int_coref(DIR + '/' + filename)
        except KeyError as err:
            print("Warning: KeyError", err, "at file:",
                  filename, file=sys.stderr)

        # Printing in markdown text format
        if len(output) > 0:
            print("### File:", filename +"\n")
            for o in output:
                print(" *", o[0]+":", o[1],"\n")
                print("\t",o[2],"\n")
            
