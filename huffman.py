import os
import sys
import marshal
import array


try:
    import cPickle as pickle
except:
    import pickle

binary_dict ={}
binary_dict_reverse = {}

def getHuffCode(tree, binary_representation):
    if(len(tree)>1):
        left = tree[0]
        right = tree[1]
        left_binary_representation =binary_representation+'0'
        right_binary_representation=binary_representation+'1'
        getHuffCode(left, left_binary_representation)
        getHuffCode(right, right_binary_representation)
    else:
        binary_dict[binary_representation]=tree
        binary_dict_reverse[tree] = binary_representation


def code(msg):

    counts ={}
    for c in msg:
        if(counts.has_key(c)):
            counts[c] = counts[c]+1
        else:
            counts[c] = 1

    ring = []
    for key in counts:
        ring.append( (counts[key], key) )

    ring=sorted(ring, key=lambda x: x[0])

    #print(ring)
    tree = ()
    left=""
    right=""

    #while(len(ring)> 1):
        #ring = sorted(ring, key=lambda x: x[0])

    #make the tree
    while(len(ring) != 0):
        #print(tree)
        if(tree == ()):

            left_left = ring.pop(0)
            left_right = ring.pop(0)

            right_left = ring.pop(0)
            right_right = ring.pop(0)

            tree = ( (left_left[0]+left_right[0], (left_left[1],left_right[1])), ( (right_left[0]+right_right[0]), (right_left[1],right_right[1])) )



        else:
            t1= ring.pop(0)
            if(tree[0][0]<tree[1][0]):
                new_sum = tree[0][0] + t1[0]

                t2 = tree[0][1]
                if(len(tree[0][1][1]) == 1):
                    tree = ( (new_sum, (t1[1], t2)) , tree[1])
                else:
                    tree = ( (new_sum,( t2,t1[1])) , tree[1])
            else:
                new_sum = tree[1][0] + t1[0]
                t2 = tree[1][1]
                if(len(tree[1][1][1]) == 1):
                    tree = (tree[0], (new_sum, ( t1[1],t2) ))
                else:
                    tree = (tree[0], (new_sum, ( t2, t1[1])))


    left = tree[0][1]
    right = tree[1][1]
    tree=(left,right)

    getHuffCode(tree,"")




    binary_representation = ""

    for c in msg:
        binary_representation+= binary_dict_reverse[c]


    return binary_representation,binary_dict
    #raise NotImplementedError

def decode(msg, decoderRing):

    decoded_msg =""
    temp=""
    for c in msg:
        temp+=c
        if(decoderRing.has_key(temp)):
            decoded_msg += decoderRing[temp]
            temp=""

    return decoded_msg




def compress(msg):

    bitmsg, binary_dict = code(msg)
    compressed = array.array('B')
    counter = 0
    buf=0

    for c in bitmsg:
        if(c =='0'):
            buf=(buf<<1)
        else:
            buf=(buf<<1)|1
            counter+=1
        if(counter >= 8 ):
            buf=0
            counter=0
            compressed.append(buf)

    print(compressed)

    return (compressed, binary_dict)

def decompress(msg, decoderRing):

    #print (msg)
    #print(decoderRing)
    byteArray = array.array('B',msg)
    print(byteArray)
    counter =0
    buf = 0
    decompressed = ""

    for i in range(len(byteArray), 0 ,-1):
        if(byteArray[i]==0):
            buf = (buf>>1)
        else:
            buf = (buf>>1) & 1
        if(decoderRing.has_key(buf)):
            decompressed+=decoderRing[buf]
            buf=0
    return decode(decompressed, decoderRing)



def usage():
    sys.stderr.write("Usage: {} [-c|-d|-v|-w] infile outfile\n".format(sys.argv[0]))
    exit(1)

if __name__=='__main__':
    if len(sys.argv) != 4:
        usage()
    opt = sys.argv[1]
    compressing = False
    decompressing = False
    encoding = False
    decoding = False
    if opt == "-c":
        compressing = True
    elif opt == "-d":
        decompressing = True
    elif opt == "-v":
        encoding = True
    elif opt == "-w":
        decoding = True
    else:
        usage()

    infile = sys.argv[2]
    outfile = sys.argv[3]
    assert os.path.exists(infile)

    if compressing or encoding:
        fp = open(infile, 'rb')
        msg = fp.read()
        fp.close()
        if compressing:
            compr, tree = compress(msg)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), compr), fcompressed)
            fcompressed.close()
        else:
            enc, tree = code(msg)
            print(msg)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), enc), fcompressed)
            fcompressed.close()
    else:
        fp = open(infile, 'rb')
        pickleRick, compr = marshal.load(fp)
        tree = pickle.loads(pickleRick)
        fp.close()
        if decompressing:
            msg = decompress(compr, tree)
        else:
            msg = decode(compr, tree)
            print(msg)
        fp = open(outfile, 'wb')
        fp.write(msg)
        fp.close() 
