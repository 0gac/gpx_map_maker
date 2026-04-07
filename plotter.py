import tools as tl
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import datetime
import contextily as cx


def plottrack(gpx: tl.GpxReadout,
              outpath: str,
              timeinput: np.ndarray = None,
              verbose=False,
              leg_pos="lower left",
              manual_img = None,
              basemap_zoom = None):

    fig, ax = plt.subplots()

    if basemap_zoom is not None:
        app_dict = {'s': 3, 'alpha': .2}
    else: 
        app_dict = {'s': 5, 'alpha': 1}

    # plotting of the route, if present w elevation color map
    if gpx.numele != 0:
        plot = ax.scatter(gpx.coordinate[:, 1], gpx.coordinate[:, 0],
                          c=gpx.ele, cmap='winter', 
                          **app_dict)
        handles, labels = plot.legend_elements(prop="colors", alpha=0.3)
        ax.legend(handles, labels, loc=leg_pos, title="altitudine", prop={'size': 6})
    else:
        ax.scatter(gpx.coordinate[:, 1], gpx.coordinate[:, 0],
                   **app_dict)
    
    if basemap_zoom is not None:
        cx.add_basemap(ax, source=cx.providers.OpenTopoMap, zoom=basemap_zoom, crs='EPSG:4326', attribution_size=5, interpolation = 'none')

    # formatting of the axes
    ax.tick_params(
        axis="both",
        which="both",
        bottom=False,
        left=False,
        labelbottom=False,
        labelleft=False
    )

    # plotting of the start and end points
    startpoint = np.reshape(gpx.coordinate[gpx.times == min(gpx.times)], 2)
    endpoint = np.reshape(gpx.coordinate[gpx.times == max(gpx.times)], 2)
    ax.scatter(startpoint[1], startpoint[0], s=60, color='green')
    ax.scatter(endpoint[1], endpoint[0], s=60, color='red')

    # plotting of the time input points
    count_images = 0
    if timeinput is not None:
        timeinput = np.array([datetime.time.fromisoformat(x) for x in timeinput])

        for ts in timeinput:
            ubtime = datetime.time(hour=ts.hour, minute=ts.minute, second=59)
            lbtime = datetime.time(hour=ts.hour, minute=ts.minute, second=0)
            coord_time = gpx.coordinate[np.logical_and(gpx.times > lbtime, gpx.times < ubtime)]
            pointpos = np.average(coord_time[:, 0:2], axis=0)

            count_images += 1
            ax.annotate(str(count_images), xy=(pointpos[1], pointpos[0]), xytext=(30, 30),
                        textcoords='offset points',
                        color='k', size='large',
                        arrowprops=dict(
                        arrowstyle='simple,tail_width=0.2,head_width=0.8,head_length=0.8',
                        color='k'))

    if  manual_img is not None:
        print("Click on the points where you want to add annotations")
        global click_counter
        click_counter = 0
        # function to get the coordinates of the clicked points
        def onclick(event):
            global click_counter
            print(click_counter)
            ix, iy = event.xdata, event.ydata
            print(click_counter, ix, iy)
            click_counter += 1
            ax.annotate(str(click_counter), xy=(ix, iy), xytext=(30, 30),
                        textcoords='offset points',
                        color='k', size='large',
                        arrowprops=dict(
                        arrowstyle='simple,tail_width=0.2,head_width=0.8,head_length=0.8',
                        color='k'))
            fig.canvas.draw()
            if click_counter == manual_img:
                fig.canvas.mpl_disconnect(cid)
                plt.close(fig)
        cid = fig.canvas.mpl_connect('button_press_event', onclick)
        plt.show()

    fig.savefig(outpath + 'track.png', bbox_inches="tight")
    if verbose:
        track_extremes = gpx.get_extremes()
        print("ora di inizio, altitudine iniziale | ora di fine, altitudine finale")
        print(track_extremes['exttimes'][0], ", ", track_extremes['extele'][0], " | ",
              track_extremes['exttimes'][1], ", ", track_extremes['extele'][1])
    return count_images


def plotmultiday(gpxs: list, outpath: str, verbose=False, basemap_zoom=None):
    tracks = []
    tracks_ele = []
    tracks_extremes = []
    for gpx in gpxs:
        tracks.append(gpx.coordinate)
        tracks_ele.append(gpx.ele)
        tracks_extremes.append(gpx.get_extremes())

    fig, ax = plt.subplots()
    ax.tick_params(
        axis="both",
        which="both",
        bottom=False,
        left=False,
        labelbottom=False,
        labelleft=False
    )    

    if basemap_zoom is not None:
        app_dict = {'s': 3, 'alpha': .2}
    else: 
        app_dict = {'s': 5, 'alpha': 1}

    counter = 0
    for t, e in zip(tracks, tracks_ele):
        ax.scatter(t[:, 1], t[:, 0], c=e, cmap="winter", **app_dict)
        counter += 1
    
    if basemap_zoom is not None:
        cx.add_basemap(ax, source=cx.providers.OpenTopoMap, zoom=basemap_zoom, crs='EPSG:4326', attribution_size=5, interpolation = 'none')

    counter = 0
    for e in tracks_extremes:
        ax.scatter(e['startcoords'][1], e['startcoords'][0], s=60, c='k')
        ax.scatter(e['endcoords'][1], e['endcoords'][0], s=60, c='k')
        # adding "notte numero " annotation
        if counter != len(tracks_extremes) - 1:
            label = "Notte " +\
                    str(counter + 1) +\
                    "\n" + str(e['extdays'][1].day) +\
                    "/" + str(e['extdays'][1].month) +\
                    "/" + str(e['extdays'][1].year)
            ax.annotate(label, xy=(e['endcoords'][1], e['endcoords'][0]), xytext=(30, 30),
                        textcoords='offset points',
                        color='k', size='large',
                        arrowprops=dict(
                        arrowstyle='simple,tail_width=0.2,head_width=0.8,head_length=0.8',
                        color='k'),
                        weight='bold')
        counter += 1

    fd = [te['extdays'][0] for te in tracks_extremes]  # first days
    ld = [te['extdays'][1] for te in tracks_extremes]  # last days
    endcoords = [te['endcoords'] for te in tracks_extremes]  # end coord for each day
    startcoords = [te['startcoords'] for te in tracks_extremes]  # stard coord for each day

    # start coord for the first day
    startcoordstot = [s for s, f in zip(startcoords, fd) if f == min(fd)][0]
    # end coord for the last day
    endcoordstot = [e for e, l in zip(endcoords, ld) if l == max(ld)][0]

    ax.scatter(endcoordstot[1],  # end of the last day
               endcoordstot[0],
               s=90, c='r')
    ax.scatter(startcoordstot[1],  # start of the first day
               startcoordstot[0],
               s=90, c='g')

    fig.savefig(outpath + 'multidaytrack.png', bbox_inches="tight")
    plt.close(fig)
    if verbose:
        print("ora di inizio, altitudine iniziale | ora di fine, altitudine finale")
        for te in tracks_extremes:
            print(te['exttimes'][0], ", ", te['extele'][0], " | ",
                  te['exttimes'][1], ", ", te['extele'][1])
    return 0


def plothr(gpx: tl.GpxReadout, outpath: str):
    if gpx.numhr != 0:
        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: gpx.convert_elap(x)))
        ax.spines[['top', 'right']].set_visible(False)
        ax.set_xlabel('Time [H:M:S]')
        ax.set_ylabel('Heart rate [BPM]')
        ax.grid()
        ax.plot(gpx.elap_time, gpx.hr, color='red')
        fig.savefig(outpath + 'hr.png')
        plt.close(fig)
        return 0
    else:
        return -1


def plotele(gpx: tl.GpxReadout, outpath: str):
    if gpx.numele != 0:
        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: gpx.convert_elap(x)))
        ax.spines[['top', 'right']].set_visible(False)
        ax.set_xlabel('Time [H:M:S]')
        ax.set_ylabel('Elevation [m SLM]')
        ax.grid()
        ax.plot(gpx.elap_time, gpx.ele, color='green')
        fig.savefig(outpath + 'ele.png')
        plt.close(fig)
        return 0
    else:
        return -1

