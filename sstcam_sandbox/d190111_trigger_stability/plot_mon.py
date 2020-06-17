import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

spdata = np.loadtxt('/Volumes/gct-jason/data_checs/d190111_trigger_stability/trigger.dat', skiprows=1)
sptimes = np.asarray(spdata[:, 0], dtype=np.float) / 60**2
sptimes -= sptimes[0]
spcounts = spdata[:, 1:513]

# for sp in range(0, 512):
#    rate = np.asarray(spcounts[:, sp], dtype=np.float)
#    if rate.mean() > 400:  # 440 and rate.mean() < 500:
#        if rate.std() < 5:
#            print(sp, rate.std(), rate.mean())


# sp2plot = np.arange(0, 512)  # [498, 101, 508, 384]
sp2plot = [151, 101, 399, 296, 145]
spcounts2plot = []
nhi = 0
nlo = 0
for sp in sp2plot:
    spcounts2plot.append(np.asarray(spcounts[:, sp], dtype=np.float))
    r = spcounts2plot[-1]
    if r.mean() < 400:
        print("SP ", sp, " LO ", r.mean())
        nlo += 1

    if r.mean() > 500:
        print("SP ", sp, " HI ", r.mean())
        nhi += 1
    plt.plot(sptimes, spcounts2plot[-1], 'o', markersize=2,
             linestyle='-', linewidth=1)

print('NLO=', nlo)
print('NHI=', nhi)

plt.show()
exit()

run_numbers = np.arange(5780, 5800)
fnames = []
for run in run_numbers:
    fnames.append("/Volumes/gct-jason/data_checs/d190111_trigger_stability/Run%05i.mon" % run)

dev_list = ['SB', 'CH']
item_list = ['T_AMBIENT', 'T_SET', 'T_WATER_OUT',
             'TMON_EX2', 'TMON_EX3', 'TMON_EX4', 'TMON_EX5', 'TMON_FAN1']

val_list = []
time_list = []
for item in item_list:
    val_list.append([])
    time_list.append([])

for fname in fnames:
    f = open(fname, 'r')
    for line in f:
        line_s = line.split(' ')
        if len(line_s) > 3:
            dev = line_s[2]
            item = line_s[3]
            if dev in dev_list:
                if item in item_list:

                    val = float(line_s[4].strip())
                    val_list[item_list.index(item)].append(val)

                    # 2019-01-07 00:47:42:236
                    timestring = line_s[0] + ' ' + line_s[1]
                    tnow = datetime.strptime(
                        timestring, '%Y-%m-%d %H:%M:%S:%f')
                    if len(time_list[0]) == 0:
                        t0 = tnow
                    dt = (tnow-t0).total_seconds() / 60.0**2.
                    time_list[item_list.index(item)].append(dt)

    f.close()


##### Temp. vs. Time ###########################################################

fig = plt.figure(figsize=(18, 12))
col = ['LightBlue', 'DarkGrey', 'LightGreen',
       'Red', 'Blue', 'Green', 'Magenta', 'Purple']
# -----FULL RANGE----------------------------------------------------------------
fig.add_subplot(2, 1, 1)
for i, item in enumerate(item_list):
    x = time_list[i]
    y = val_list[i]
    markeredgecolor = col[i]
    if i < 2:
        markeredgecolor = 'gray'
    plt.plot(x, y, 'o', markersize=2, markeredgecolor=markeredgecolor,
             markeredgewidth=1, color=col[i], alpha=0.7, label=item)

plt.ylabel("Temp. (C)")
plt.xlabel("dt (hours)")
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(True)

for sp in spcounts2plot:
    plt.plot(sptimes, sp/20, '+', markersize=2,
             linestyle='-', linewidth=1, color='black')

lgnd = plt.legend(loc=1, prop={'size': 10}, numpoints=1,
                  scatterpoints=1, markerscale=3, ncol=1)


# -----ZOOM----------------------------------------------------------------------
fig.add_subplot(2, 1, 2)
for i, item in enumerate(item_list):
    x = time_list[i]
    y = val_list[i]
    plt.plot(x, y, 'o', markersize=2, markeredgecolor='gray',
             markeredgewidth=0.5, color=col[i], alpha=0.7, label=item)

plt.ylabel("Temp. (C)")
plt.xlabel("dt (hours)")
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(True)

for sp in spcounts2plot:
    plt.plot(sptimes, sp/20, '+', markersize=2,
             linestyle='-', linewidth=1, color='black')


plt.xlim(0, 1)

##### Temp vs. Rate SP 5 #######################################################

fig = plt.figure(figsize=(18, 6))
col = ['LightBlue', 'DarkGrey', 'LightGreen',
       'Red', 'Blue', 'Green', 'Magenta', 'Purple']
a = 4000
b = 4200
mt = time_list[0][a:b]
rt = sptimes
# For each rate point match up the closest mon point
xr = np.zeros(len(mt))  # Rate!
for i in range(len(mt)):
    for j in range(len(rt)-1):
        if (mt[i] >= rt[j]) and (mt[i] < rt[j+1]):
            #print (mt, rt, rate[j])

            xr[i] = spcounts2plot[0][j]  # SP 5 rates

print(xr[0:10],  val_list[0][0:10])
print(xr[200:210],  val_list[0][200:210])
print('Original rate', len(spcounts2plot[0]))
print('Original mon', len(mt))
print('New rate', len(xr))
print('mon val', len(val_list[0]))

#plt.plot(mt, xr/20 - 6, 'o', markersize=6, linestyle='-', linewidth=1, color='Grey')
#plt.plot(mt, xr/20 - 6, 'o', markersize=6, linestyle='-', linewidth=1, color='Red')
#plt.plot(time_list[0], val_list[2], 'o', markersize=3, linestyle='-', linewidth=1, color='green')

for i, item in enumerate(item_list):

    y = np.asarray(val_list[i][a:b])
    y = (y - np.mean(y))

    markeredgecolor = col[i]
    if i < 2:
        markeredgecolor = 'gray'

    plt.plot(y, xr, 'o', markersize=4, markeredgecolor=markeredgecolor,
             markeredgewidth=1, color=col[i], alpha=0.7, label=item)

    if i == 2:

        denom = xr.dot(xr) - xr.mean() * xr.sum()
        m = (xr.dot(y) - y.mean() * xr.sum()) / denom
        c = (y.mean() * xr.dot(xr) - xr.mean() * xr.dot(y)) / denom

        ypred = m*xr + c

        plt.plot(ypred, xr)

print("Temp = %0.2f x Rate + %0.2f" % (m, c))
mm = 1. / m
cc = -c / m
print("Rate = %0.2f x Temp + %0.2f" % (mm, cc))

plt.xlabel("Temp. (C)")
plt.ylabel("Rate SP5")
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
# plt.xlim(2,4)
# plt.ylim(13,16)
plt.grid(True)


plt.show()
