'''Decompressing the compressed temp TIMD and putting it into a dictionary'''
#potential keys for the dictionary to be made
COMPRESSKEY = {
    'a': 'startingLevel',
    'b': 'crossedHabLine',
    'c': 'startingLocation',
    'd': 'preload',
    'e': 'driverStation',
    'f': 'isNOShow',
    'g': 'timerStarted',
    'h': 'currentCycle',
    'j': 'scoutID',
    'k': 'scoutName',
    'm': 'appVersion',
    'n': 'appVersion',
    'p': 'assignmentFileTimeStamp',
    'q': 'matchesNotScouted',
}
#potential values for the keys of the dictionary about to be made
COMPRESSVALUE = {
    'T': True,
    'F': False,
    'A': 'left',
    'B': 'mid',
    'C': 'right',
    'D': 'far',
    'E': 'orange',
    'G': 'lemon',
    'H': 'none',
    'J': 'QR',
    'K': 'backup',
    'L': 'override',
    'M': 'intake',
    'N': 'placement',
    'P': 'drop',
    'Q': 'spill',
    'R': 'climb',
    'S': 'incap',
    'U': 'unincap',
    'V': 'zone1Left',
    'W': 'zone1Right',
    'X': 'zone2Left',
    'Y': 'zone2Right',
    'Z': 'zone3Left',
    'a': 'zone3Right',
    'b': 'zone4Left',
    'c': 'zone4Right',
    'd': 'leftLoadingStation',
    'e': 'rightLoadingStation',
    'f': 'leftRocket',
    'g': 'rightRocket',
    'h': 'cargoShip',
    'j': 'tippedOver',
    'k': 'brokenMechanism',
    'm': 'stuckOnObject',
    'n': 'stuckOnHab',
    'p': 'emergencyStop',
    'q': 'noControl',
    'r': 'twoGamePieces',
}
#compressed data
SCOUTEDDATA = '1678Q1-3|a2,bT,cB,dG,e1,fF,g1547528330,h4,j7,kD,m1.2,nJ,p1547528290,q[1;14;28;35]_rMs102.4tEuevTwF,rSs109.6Ak,rUs111.1,rPs112.1tE,rMs127.4tGvFwFxfyCz2,rQs130tG,rRs138B{D3;E3;F2}C{D3;E2;F1}'
#splitting the compressed data to isolate the headers
SPLIT = SCOUTEDDATA.split('|')[1]
HEADER = SPLIT.split('_')[0]
HEADERVAL = HEADER.split(',')

#The dictionary that all the information goes in
DECOMPRESSEDHEADERS = {}

for item in HEADERVAL:
    key = item[0]
    value = item[1:]
    UNCOMPRESSKEY = COMPRESSKEY[key]
#determines if the item starts with a 'q'
#if item does, it divides the list by the ';'
#than it puts item into a new list
    if item[0] == 'q':
        MATCHES = item[2:-1]
        NOSCOUT = [int(MATCHNUM) for MATCHNUM in MATCHES.split(';')]
        DECOMPRESSEDHEADERS[UNCOMPRESSKEY] = NOSCOUT
#other wise it checks if the item is one digit and a letter
#if item is, it is decompressed an added to the dictionary
    elif len(value) == 1 and value.isalpha() is True:
        DECOMPRESSEDHEADERS[UNCOMPRESSKEY] = COMPRESSVALUE[value]
#if item doesn't fit there it is stored as an integer
    elif value.isdigit() is True:
        DECOMPRESSEDHEADERS[UNCOMPRESSKEY] = int(value)
#otherwise item is added as a float
    else:
        DECOMPRESSEDHEADERS[UNCOMPRESSKEY] = float(value)
#displays dictionary
print(DECOMPRESSEDHEADERS)
