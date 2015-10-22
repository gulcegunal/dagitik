import threading, time, Queue
import sys

alphabet = "abcdefghijklmnopqrstuvwxyz"
newAlphabet = ""
cryptedText = ""
exitFlag = 0
blocknumber = 0
row = 0
s = int(input("Enter the shifting parameter,s: "))
n = int(input("Enter the number of threads,n: "))
l = int(input(" Enter the block length,l: "))

class myThread (threading.Thread):
    global  newAlphabet, readFile, writeFile

    def __init__ (self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print ("Starting " + self.name)
        caesarCipher(self.name, l, newAlphabet, readFile, writeFile)
        print ("Exiting " + self.name)


def key(s):
    global newAlphabet
    for i in range(len(alphabet)):
        newAlphabet += alphabet[i-s].upper()


def caesarCipher(threadName, l, newAlphabet, readFile, writeFile):
    global cryptedText, blocknumber, row
    while True:
        queueLock.acquire()
        r = readFile.read(l)
        if( r != ""):
           text = r.lower()
           myBlock = blocknumber
           blocknumber +=l
           queueLock.release() 
        else:
           queueLock.release()  
           break
        print "%s encodes %s" % (threadName, text)
        for i in range(len(text)):
            for j in range(len(alphabet)):
                if (text[i] == alphabet[j]):
                    cryptedText += newAlphabet[j]
                elif not(text[i] in alphabet):
                    cryptedText += text[i]
                    break
        while not(myBlock == row):
            pass      
        queueLock.acquire()
        writeFile.write(cryptedText.upper())
        cryptedText= ""
        row = row+l
        queueLock.release()
        time.sleep(1)
 


key(s)
print (alphabet)
print (newAlphabet)

try:
    global readFile,writeFile,writingFileName
    readFile = open("metin.txt","r")
    writingFileName = "crypted_"+str(s)+"_"+str(n)+"_"+str(l)+".txt"
    writeFile = open(writingFileName,"w")
except:
    print "File does not exist!"
    sys.exit()

queueLock = threading.Lock()
threads = []
threadList = []
threadID = 1

for i in range (1,n+1):
   threadList.append("Thread-"+str(i)) 

for tName in threadList:
   thread = myThread(threadID, tName)
   thread.start()
   threads.append(thread)
   threadID +=1


for t in threads:
    t.join()

print ("Exiting Main Thread")

readFile.close()
writeFile.close()
