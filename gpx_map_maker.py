import sys

import plotter as pl
import tools as tl


def main():

    multiday = False

    args = tl.parse_args(sys.argv)
    # input path
    if "p" in args:
        if len(args["p"]) != 1:
            multiday = True
        path = args["p"]
    else:
        print("No input file")
        return -1

    # output path
    if "op" in args:
        if len(args["op"]) != 1:
            print("Too many output paths")
            return -1
        outpath = args["op"][0]
    else:
        outpath = ""

    # time strings
    if "t" in args:
        timestrings = args["t"]
    else:
        timestrings = []

    # verbose
    if "v" in args:
        verbose = True
    else:
        verbose = False

    # legend position: lower/upper left/right
    if "lp" in args:
        leg_pos = ""
        for w in args["lp"]:
            leg_pos += w
            leg_pos += " "
        leg_pos = leg_pos[:-1]
    else:
        leg_pos = "lower left"

    # manual addition of points on the track
    if "mi" in args:
        assert len(args["mi"]) == 1
        manual_img = int(args["mi"][0])
    else:
        manual_img = None

    # basemap
    if "bm" in args:
        if len(args["bm"]) == 1:
            basemap_zoom = int(args["bm"][0])
        elif len(args["bm"]) == 0:
            if multiday:
                basemap_zoom = 14
            else:
                basemap_zoom = 15
        else:
            print("Too many basemap zoom values")
            return -1
    else:
        basemap_zoom = None

    # execution
    if not multiday:
        gpx = tl.GpxReadout(path[0])
        pl.plottrack(
            gpx,
            outpath,
            timeinput=timestrings,
            verbose=verbose,
            leg_pos=leg_pos,
            manual_img=manual_img,
            basemap_zoom=basemap_zoom,
        )
        hashr = 0
        hasele = 0
        print(gpx.numhr)
        print(gpx.numele)
        if gpx.numhr != 0:
            pl.plothr(gpx, outpath)
            hashr = 1
        if gpx.numele != 0:
            pl.plotele(gpx, outpath)
            hasele = 1
        return hashr, hasele

    else:
        gpxs = [tl.GpxReadout(p) for p in path]
        pl.plotmultiday(gpxs, outpath, verbose=verbose, basemap_zoom=basemap_zoom)


if __name__ == "__main__":
    main()
