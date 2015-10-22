from multiprocessing import Lock, Process, Queue, current_process
import time

lock = Lock()
alphabet = "abcdefghijklmnopqrstuvwxyz"
newAlphabet = ""
cryptedText = ""
cryptedTemp = ""
turn = 0
row = 0
def worker(work_queue, done_queue):
    global turn
    for word in iter(work_queue.get,"STOP"):
        myTurn = turn
        turn +=1
        cipher(word, done_queue, myTurn)
        print("%s-%s" % (current_process().name, word))
    return True

def key(s):
    global newAlphabet, cryptedTemp
    for i in range(0,len(alphabet)):
        newAlphabet += alphabet[i-s]

def cipher(word,done_queue, myTurn):

    global cryptedText, row
    word = word.lower()
    for i in range(0,len(word)):
        for j in range(0,len(alphabet)):
            if (word[i] == alphabet[j]):
                cryptedText += newAlphabet[j]
            elif not(word[i] in alphabet):
                cryptedText += word[i]
                break
    while not ( myTurn == row):
        pass
    lock.acquire()
    done_queue.put(cryptedText.upper())
    cryptedText =""
    row +=1
    lock.release()
    time.sleep(1)


def main():
    s = int(input("Enter the number of threads ,s: "))
    n = int(input("Enter the shifting parameter,n: "))
    l = int(input(" Enter the block length,l: "))

    work_queue = Queue()
    done_queue = Queue()
    processes = []
    wordList = []
    key(s)
    readFile = open("metin.txt","r")
    writingFileName = "crypted_"+str(s)+"_"+str(n)+"_"+str(l)+".txt"
    writeFile = open(writingFileName,"w")

    r = readFile.read(l)
    while( r!= ""):
       wordList.append(r)
       r= readFile.read(l)

    for word in wordList:
       work_queue.put(word)

    for w in xrange(n):
        p = Process(target= worker, args=(work_queue, done_queue))
        p.start()
        processes.append(p)
        work_queue.put("STOP")

    for p in processes:
        p.join()

    done_queue.put("STOP")

    for newWord in iter(done_queue.get,"STOP"):
        writeFile.write(newWord)
    writeFile.close()
if __name__ == "__main__":
    main()

