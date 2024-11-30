import yaml
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.animation import FuncAnimation
from matplotlib import dates
from pythonping import ping
import datetime
import itertools


config = yaml.safe_load(open("config.yaml"))
target_address = config["ping_target"]
timeout = config["packet_ttl"]
dark_mode = config["dark_mode"]
maxtime = 200
start_time = datetime.datetime.now()

plt.rcParams["toolbar"] = "None"
if dark_mode:
    plt.style.use("dark_background")
    mpl.rcParams.update({"grid.color": "gray"})
fig, ax = plt.subplots()
(line,) = ax.plot([], [], lw=2)
myFmt = dates.DateFormatter('%H:%M:%S')
ax.xaxis.set_major_formatter(myFmt)
ax.grid()
xdata, ydata = [], []


def ping_target() -> float:
    result = ping(target_address, timeout=timeout)
    if result.rtt_max_ms >= timeout * 1000:
        return result.rtt_max_ms
    return (result.rtt_max_ms + result.rtt_min_ms) / 2


def data_gen():
    for cnt in itertools.count():
        t = datetime.datetime.now()
        yield t, [ping_target()]


def init():
    ping_data = []
    ax.set_ylim(40, 50)
    ax.set_xlim(0, 100)
    del xdata[:]
    del ydata[:]
    line.set_data(xdata, ydata)
    return (line,)


def run(data):
    # Обновляем данные
    t, y = data
    xdata.append(t)
    ydata.append(y)
    right_limit = datetime.timedelta(seconds=10)
    left_limit = datetime.timedelta(minutes=1)

    ytemp = [i[0] for i in ydata]
    ax.set_ylim(min(ytemp) - 10, max(ytemp) + 10)

    if t < start_time + left_limit:
        ax.set_xlim(start_time, t + right_limit)
    else:
        ax.set_xlim(t - left_limit, t + right_limit)
    ax.xaxis.set_major_locator(plt.MaxNLocator(4))
    if len(xdata) > 0:
        xtime = dates.date2num(xdata)
    else:
        xtime = []
    line.set_data(xtime, ydata)
    if line is not None:
        line.set_color('red')

    return (line,)


ani = FuncAnimation(
    fig,
    run,
    data_gen(),
    interval=100,
    init_func=init,
    cache_frame_data=False,
)

plt.show()
