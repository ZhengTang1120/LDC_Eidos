import json
import csv

def intersection(lst1, lst2): 
    return list(set(lst1) & set(lst2))

j1 = json.load(open('/Users/zheng/Documents/CausalAssertions/LDC2019E61_Events_Simple_and_Complex_Cause_Assertion_Annotation_Training_Data_Set_1/training_set.json'))
j2 = json.load(open('/Users/zheng/Downloads/eidos-master/output/training_set.json'))

count = 0
with open('false.csv', 'w', newline='') as csvfile:
    fieldnames = ['docId', 'sentence', 'eidos_cause', 'eidos_effect', 'LDC_cause', 'LDC_effect']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for item in j2:
        no_match = True
        for item2 in j1:
            if item[0] == item2[0]:
                if float(len(intersection(item[2], item2[2])))/float(len(item[2]))>0.6:
                # a = ''.join(item[2]).replace(' ', '')
                # b = ''.join(item2[2]).replace(' ', '')
                # if not (a == b):
                #     print (a)
                #     print (b)
                #     print
#                 if (len(intersection(item[3], item2[3]))>0 and len(intersection(item[4], item2[4]))>0):
#                     count += 1
# print count
        #             no_match = False
        #             break
        # if no_match:
        #     writer.writerow({
        #         'docId': item[0],
        #         'sentence': ' '.join(item[2]), 
        #         'eidos_cause': ' '.join(item[2][item[3][0]: item[3][-1]+1])+' '+str(item[3]), 
        #         'eidos_effect': ' '.join(item[2][item[4][0]: item[4][-1]+1])+' '+str(item[4]),
        #         }) 
                    if  not (len(intersection(item[2][item[3][0]: item[3][-1]+1], item2[2][item2[3][0]: item2[3][-1]+1]))>0 and len(intersection(item[2][item[4][0]: item[4][-1]+1], item2[2][item2[4][0]: item2[4][-1]+1]))>0):
#                         count += 1
# print (count)
                            writer.writerow({
                                'docId': item[0],
                                'sentence': item2[2], 
                                'eidos_cause': ' '.join(item[2][item[3][0]: item[3][-1]+1])+' '+str(item[3]), 
                                'eidos_effect': ' '.join(item[2][item[4][0]: item[4][-1]+1])+' '+str(item[4]),
                                'LDC_cause': ' '.join(item2[2][item2[3][0]: item2[3][-1]+1])+' '+str(item2[3]), 
                                'LDC_effect': ' '.join(item2[2][item2[4][0]: item2[4][-1]+1])+' '+str(item2[4])}) 


