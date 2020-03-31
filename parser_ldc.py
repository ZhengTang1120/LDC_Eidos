import xml.etree.ElementTree as ET
import csv
import os
import glob
from collections import defaultdict
import string
import pickle
import json
import itertools
import random

def locate(doc, token):
    for i, seg in enumerate(doc):
        if token[1] <= seg[-1][2] and seg[0][1] <= token[2]:
            span = []
            for j, t in enumerate(seg):
                if t[1] <= token[2] and token[1] <= t[2]:
                    span.append(j)
            return i, span

def parse_causes(file, lft, events):
    dist=defaultdict(int)
    ans = list()
    with open(file) as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='\t', quotechar='"')
        for row in spamreader:
            sid = row['source_uid']
            if sid not in lft:
                doc = lft[sid[:-3]]
            else:
                # continue
                doc = lft[sid]
            # connector = (row['connector_text'], row['connector_beg'], row['connector_end'])
            cause = events[sid][row['cause_evm_id']]
            effect = events[sid][row['effect_evm_id']]
            cid, cspan = locate(doc, cause)
            eid, espan = locate(doc, effect)
            start = min(cid, eid)
            end = max(cid, eid)
            dist[(end-start)]+=1
            text = []
            for i, sentence in enumerate(doc[start:end+1]):
                if i == end-start:
                    if cid>eid:
                        cspan = [c + len(text) for c in cspan]
                    else:
                        espan = [e + len(text) for e in espan]
                text += [t[0] for t in sentence]

            if row['type'] != 'hastopic':
                ans.append((sid, row['type'], text, cspan, espan))
    return ans, dist
                

def parse_events(file):
    res = defaultdict(dict)
    with open(file) as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='\t', quotechar='"')
        offsets = dict()
        for row in spamreader:
            offset = 0
            if '_a' in row['source_uid'] and '_aa' not in row['source_uid']:
                if row['source_uid'] in offsets:
                    offset = offsets[row['source_uid']]
                else:
                    with open('data/source/rsd/'+row['source_uid']+'.rsd.txt') as f:
                        content = f.read()
                        query = content.split('.')[0].strip().split('\n')[0].encode("ascii", errors="ignore").decode()
                        tree = ET.parse('data/source/ltf/'+row['source_uid'][:-3]+'.ltf.xml')
                        root = tree.getroot()
                        for child in root[0][0]:
                            if 'ENG_NA_999999_20180000_000000051' in row['source_uid'] and query == '2005':
                                offsets[row['source_uid']] = 30213
                                offset = 30213
                                break
                            if 'ENG_NA_999999_20180000_000000051' in row['source_uid'] and query == 'This content downloaded from 129':
                                offsets[row['source_uid']] = 5544
                                offset = 5544
                                break
                            if query == '10' and child[0].text.encode("ascii", errors="ignore").decode() == query:
                                offsets[row['source_uid']] = int(child.get('start_char'))
                                offset = int(child.get('start_char'))
                                break
                            if query != '10' and child[0].text.encode("ascii", errors="ignore").decode().startswith(query):
                                offsets[row['source_uid']] = int(child.get('start_char'))
                                offset = int(child.get('start_char'))
                                break
            res[row['source_uid']][row['eventmention']] = (row['trigger_text'], int(row['trigger_beg'])+offset, int(row['trigger_end'])+offset)
    return res

def parse_ltf(dirname):
    res = defaultdict(list)
    for fname in glob.glob(os.path.join(dirname, '*.xml')):
        tree = ET.parse(fname)
        root = tree.getroot()

        for child in root[0][0]:
            tokens = list()
            for token in child.iter('TOKEN'):
                tokens.append((token.text, int(token.get('start_char')), int(token.get('end_char'))))
            res[os.path.basename(fname).split('.')[0]].append(tokens)
    return res

def generate_neg(lft, events, negs):
    ans = defaultdict(list)
    for row in negs:
        sid = row[0]
        if sid not in lft:
            doc = lft[sid[:-3]]
        else:
            # continue
            doc = lft[sid]
        cause = events[sid][row[1]]
        effect = events[sid][row[2]]
        cid, cspan = locate(doc, cause)
        eid, espan = locate(doc, effect)

        start = min(cid, eid)
        end = max(cid, eid)
        text = []
        for i, sentence in enumerate(doc[start:end+1]):
            if i == end-start:
                if cid>eid:
                    cspan = [c + len(text) for c in cspan]
                else:
                    espan = [e + len(text) for e in espan]
            text += [t[0] for t in sentence]
        ans[end-start].append((sid, "not_causal", text, cspan, espan))
    return ans
lft    = parse_ltf('data/source/ltf/')
events = parse_events('data/annotation/events.20190715.tab')
pairs = list()
for event in events:
    for pair in itertools.permutations(events[event],2):
            pairs.append((event, pair[0], pair[1]))
print (len(pairs))
postives = list()
with open('data/annotation/cause_assertions.20190715.tab') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='\t', quotechar='"')
        for row in spamreader:
            if row['type'] != 'hastopic':
                if ((row['source_uid'], row['cause_evm_id'], row['effect_evm_id'])) not in pairs:
                    print ((row['source_uid'], row['cause_evm_id'], row['effect_evm_id']))
                postives.append((row['source_uid'], row['cause_evm_id'], row['effect_evm_id']))
negatives = list()
print (len(postives))
for event in events:
    for pair in itertools.permutations(events[event],2):
        if (event, pair[0], pair[1]) not in postives:
                negatives.append((event, pair[0], pair[1]))
print (len(negatives))

causes, dist = parse_causes('data/annotation/cause_assertions.20190715.tab', lft, events)
not_causes_dist = generate_neg(lft, events, negatives)
not_causes = list()

for d in dist:
    print (d, len(not_causes_dist[d]), dist[d])
    try:
        not_causes += random.sample(not_causes_dist[d], dist[d]*10)
    except:
        not_causes += not_causes_dist[d]

print (len(causes+not_causes))
# with open('training_data.json', 'w') as f:
#     f.write(json.dumps(causes+not_causes))
with open('training_set.json', 'w') as f:
    f.write(json.dumps(causes))

