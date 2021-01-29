#!/usr/bin/env python3
# Cristian Garcia, Emmanuel Espinosa-Tello, Tyler Worch



#import sys to use argv (arguments that are being passed in)
import sys
import re
import random

def powers(x):
    '''simply gives you the # in powers of 2'''
    i = 0
    while x != 1 and x >= 1:
        x /= 2
        i += 1
    return i

#l = length, a = address, ca = cachearray
miss =0
hit =0
total =0
#cacheasso = {} this is a dictionary
def blockselect(index):
    '''Based on replacement policy will return a position in the cache for the tag to go in'''
    if replacement_policy == 'RR':
        ''''''
        if index in cacheasso:
            '''ROUND ROBIN each block goes in order'''
            cacheasso[index] +=1
            if cacheasso[index] > (int(associativity) - 1):
                cacheasso[index] = 0
                return cacheasso[index]
            return cacheasso[index]

        else:
            cacheasso[index] = 0
            return cacheasso[index]
    elif replacement_policy == 'RND':
        '''RANDUMB'''
        return random.randrange(int(associativity))
    else:
        print("Unknown Replacement Policy: Exiting")
        exit(1)

def checkempt(ca, index):
    for i in range(len(ca[index])):
        if ca[index][i] == 0:
            return i
    return -1

def read(l, index, offset):
    indoff = (index << b2) + offset #shift index by offset bits to make room for offset
    i = index
    newindexlist = []
    while(l != 0):
        l -= 1
        indoff +=1
        nindex = indoff >> b2
        if nindex != i:
            newindexlist.append(nindex)
            i = nindex
    return newindexlist

def indexover(index, tag, ca):
    global hit, miss
    if index in cachevalid:
        if tag in ca[index]:
            hit +=1
            #print("indexover: {}".format(hit))
            return
        else:
            miss +=1
            position = checkempt(ca, index)
            if position != -1:
                ca[index][position] = tag
                return
            else:
                position = blockselect(index)
                ca[index][position] = tag
                return
    else:
        miss +=1
        cachevalid[index] = 1
        ca[index][0] = tag
        return
        
def newindexr(inli, tag, ca):
    '''takes in result of new index'''
    global total
    if not inli:
        return

    for index in inli:
        indexover(index, tag, ca)
        total +=1
    return

#cachevalid{}, 
def cache(l, a, ca):
    '''function that sims the cache'''
    index = int(a,16) >> b2 & 2**indexbits - 1 #gives index in hex
    offset = int(a,16) & 2**b2 - 1 #gives the offset
    tag = int(a,16) >> (b2 + indexbits) #gives the tag
    #print("{} {} {}".format(index, offset, tag))
    
    global hit, miss
    #blch = blockselect(index) #blch = block chosen
    if index in cachevalid: 
        if tag in ca[index]:
            hit +=1
            #print("cache: {}".format(hit))
            newindexr(read(l, index, offset), tag, ca)
            return
        else:
            miss +=1 
            position = checkempt(ca,index)
            if position != -1:
                ca[index][position] = tag
                newindexr(read(l, index, offset), tag, ca)
                return
                #call read here
            else:
                position = blockselect(index)
                ca[index][position] = tag
                newindexr(read(l, index, offset), tag, ca)
                return
                #call read here
    else:
        miss += 1
        cachevalid[index] = 1
        ca[index][0] = tag #does not matter if index is empty will always goto first one
        newindexr(read(l, index, offset), tag, ca)
        return
        #read?

    #print("{} {} {}".format(tag, index, offset))
    return 

#We do len(sys.argv - 1) because we dont care about sim.py (sim.py –f trace1.txt –s 1024 –b 16 –a 2 –r RR)
#10 being 10 arguments
if (len(sys.argv) - 1) == 10:
    
    #for every other argument not including (sim.py) in the command line Ex. (–f) trace1.txt (–s) 1024 (–b) 16 (–a) 2 (–r) RR
    # (-f -s -b -a -r)
    
    for i in range(len(sys.argv)):
        if sys.argv[i] == "-f":
            filename = sys.argv[i+1];
        elif sys.argv[i] == "-s":
            cache_size = sys.argv[i+1];
        elif sys.argv[i] == "-b":
            block_size = sys.argv[i+1];
        elif sys.argv[i] == "-a":
            associativity = sys.argv[i+1];
        elif sys.argv[i] == "-r":
            replacement_policy = sys.argv[i+1]


    totaladdrspaceb = 32 #addr space in bits assumed to be 32
    c2 = powers(int(cache_size)) + 10 #cache in KB i.e. 1024 = 20
    b2 = powers(int(block_size)) #bytes per block in 2 i.e. 16 = 4 aka bits
    blksin2 = (c2 - b2) # #of blocks in 2 (2^20)/(2^4) = 2^16 or 16
    blksin2b = blksin2 - 10 # # of blocks rep without kilobytes i.e 16 - 10 = 2^6
    numblksKB = 2**blksin2b
    #offsetb = totaladidspaceb - b2 # example should be 32 - 4 = 28 bits remain in addr space
    abinbits = (b2 + powers(int(associativity))) #offset = block size plus associativity in bits i.e. 4 + 1 (blk size + associativty in powers of two) 
    indexbits = (c2 - abinbits) #cache size / blocksize * associativity
    trueindexsize = 2**indexbits #totalindicies for dynamic array size
    tindicies = 2**(indexbits - 10) #totalindicies is given in KB simeply converting
    tagbits = totaladdrspaceb - (b2 + indexbits) #addrspace - (offset bits + index bits) goes up with associativity
    overhead = ((tagbits + 1) * (2**blksin2))/8 #(tagbits + valid bits) * (# of blks) / 8
    imp = overhead + (2**c2) # overhead plus cache size
 
    cachearray = [[0 for j in range(int(associativity))] for i in range(trueindexsize)]
    cacheasso = {} #simply holds the block the replacement policy chose
    cachevalid = {} #is index valid, holds only 1's
    
    try:
        with open(filename, 'r') as inputFile:
        #for every line in the file

            for line in inputFile:
                if line == "\n":
                    '''''' 
                else:
                    readNextLine = 0
                    tokens = line.split();

                    # using regular expression to find non-digits (\D) and replace them with nothing A.K.A. (delete)
                    length = re.sub(r'\D', "", tokens[1])
                    address = tokens[2]
                    
                    # read the next line while still in the same iteration
                    # to grab the dstM and srcM. (this also moves the file pointer) 
                    tokens2 = inputFile.readline().split()
                    readNextLine = 1
                    
                    dstM = tokens2[1]
                    srcM = tokens2[4]
                        
                    isThereData1 = 1
                    isThereData2 = 1

                    if int(dstM, 16) == 0 and readNextLine == 1:
                        isThereData1 = 0
                    else:
                        cache(4, dstM, cachearray)
                        total +=1

                    if int(srcM, 16) == 0 and readNextLine == 1:
                        isThereData2 = 0
                    else:
                        cache(4, srcM, cachearray)
                        total +=1
                    
                    cache(int(length), address, cachearray)
                    total +=1
                    if isThereData1 == 0 and isThereData2 == 0:
                        ''''''
                        #print("Address: 0x" + address + ", length =", length, "No data writes/reads occurred.")
                    else:
                        ''''''
                        #print("Address: 0x" + address + ", length =", length, "Data write at 0x" + dstM, "length = 4 bytes.")
    except IOError:
        print("Error opening file: " + sys.argv[2] + ".")
        sys.exit(1)
        
    #print("{} {} {}".format(hit, miss, total))
    hitrate = hit/total *100
    missrate = miss/total *100

    # Print results
    print("Cache Simulator CS 3853 Spring 2019 - Group #21\n")
    print("Cmd Line:", " ".join(sys.argv))
    print("Trace File:", filename)
    print("Cache Size:", cache_size, "KB")
    print("Block Size:", block_size, "bytes")
    print("Associativity:", associativity, "way")
    print("R-Policy:", replacement_policy)
    print("")
    print("Generic:")
    print("Cache Size:", cache_size, "KB")
    print("Block Size:", block_size, "bytes")
    print("Associativity:", associativity)
    print("Policy:", replacement_policy)
    print("")
    print("----- Calculated Values -----")
    print("Total #Blocks: {} KB (2^{})".format(numblksKB, blksin2))
    print("Tag Size: {} bits".format(tagbits))
    print("Index Size: {} bits, Total Indices: {} KB".format(indexbits, tindicies))
    print("Overhead Size: {:,} bytes".format(int(overhead)))
    print("Implementation Memory Size: {:,} bytes".format(int(imp)))
    print("")
    print("----- Results -----")
    print("Cache Hit Rate: {:.4f}%".format(hitrate))
    print("Cache Miss Rate: {:.4f}%".format(missrate))
else:
    print("Error: Argument(s) not in range.")
    sys.exit(1)