import numpy
import matplotlib.pyplot as plt


s = numpy.random.normal(4, 1.5, 10000)
l = numpy.random.normal(-4, 1.2, 10000)
print(s)
print(l)

h= [0]*41
print(h)
c=0
for a in s:
    if (-21 <  a  and a <20):
     h[int(round(a))+20]   =h[int(round(a))+20]+1
     c=c+1

print (h)

for i in range(len(h)):
    h[i]=float(h[i])/ float(c)
print(h)


g= [0]*41
print(g)
c=0
for a in l:
    if (-21 <  a  and a <20):
     g[int(round(a))+20]   =g[int(round(a))+20]+1
     c=c+1

print (g)
print (c)
for i in range(len(g)):
    g[i]=float(g[i])/ float(c)
print(g)
plt.axis((-20,20,0,1))
plt.bar(range(-20,21), h,color='blue')
plt.bar(range(-20,21), g,color='pink')
plt.show()

som=0
i=0
j=0
while(i<=40 and j<=40):
    if h[i]==0:
        i=i+1
        continue
    if g[j]==0:
        j=j+1
        continue
    if h[i]<g[j]:

        dist=abs(i-j)
        som=som+dist*float(h[i])
        g[j]=g[j]-h[i]
        h[i]=0
        continue
    if h[i]>=g[i]  :
        som=som+abs(i-j)*float(g[j])
        h[i]=h[i]-g[j]
        g[i]=0
        continue



print("sonuc=",som)
