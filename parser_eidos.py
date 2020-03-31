import csv
import os
import glob
import json

count = 0
ans = list()
for fname in glob.glob(os.path.join('.', '*.jsonld')):
    d=dict()
    s=dict()
    with open(fname) as jsonfile:
        j = json.load(jsonfile)
        for doc in j['documents']:
            count += len(doc['sentences'])
            for sentence in doc['sentences']:
                s[sentence['@id']]=sentence
        if 'extractions' in j: 
            for extraction in j['extractions']:
                d[extraction['@id']]=extraction
            for extraction in j['extractions']:
                if extraction['type'] == 'relation' and extraction['subtype'] in ['causation', 'precondition', 'catalyst', 'mitigation', 'prevention']:
                    text = [w['text'] for w in s[extraction['provenance'][0]['sentence']['@id']]['words']]
                    cause = None
                    effect = None
                    for a in extraction['arguments']:
                        if a['type'] == 'source':
                            cause = d[a['value']['@id']]['provenance'][0]['sentenceWordPositions']
                        if a['type'] == 'destination':
                            effect = d[a['value']['@id']]['provenance'][0]['sentenceWordPositions']
                    cspan = (range(int(cause[0]['start'])-1, int(cause[0]['end'])))
                    espan = (range(int(effect[0]['start'])-1, int(effect[0]['end'])))
                    print (fname, extraction['subtype'], text, cspan, espan, extraction['rule'])
                    ans.append((fname, extraction['subtype'], text, cspan, espan, extraction['rule']))
print (len(ans))
with open('training_set.json', 'w') as f:
    f.write(json.dumps(ans))

print (count)


