import matplotlib.pyplot as plt
import numpy as np
import pandas

#radius = 0.15
#exact = np.pi*radius**2

def percent_error(data):
    return (data - exact) / exact * 100

def plot_area(data, radius=0.15, order=2, label=None):
    time = data['time']
    area = data['area']

    #initial = area[0]
    initial = np.pi*radius**2
    area = (area - initial) / initial * 100

    fit = np.poly1d(np.polyfit(time, area, order))
    plt.plot(time, fit(time), label=label)
    #plt.plot(time, area)

fig = plt.figure(facecolor=[1,1,1])


advec = pandas.read_csv('advection_out.csv')
advec_reinit_inline = pandas.read_csv('advection_reinit_inline_out.csv')
advec_reinit_multiapp = pandas.read_csv('multiapp/master_out.csv')

plot_area(advec, label="Advection Only")
plot_area(advec_reinit_inline, label="Inline Reinitialization")
plot_area(advec_reinit_multiapp, label="Reinitialization")

plt.grid(True)
plt.xlabel('Time')
plt.ylabel('Percent Error in Area')
plt.legend(loc='best')
plt.savefig('area.pdf')
plt.show()
