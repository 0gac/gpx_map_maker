import sys

import plotter as pl
import tools as tl


def parse_cmdline():

    out = {}

    out["multiday"] = False

    args = tl.parse_args(sys.argv)

    if "h" in args:
        print("""
usage: gpx_map_maker.py -p <file> [options]

options:
-p  <file> [file ...]   Input file(s). Multiple files treated as a multiday hike.
-op <file>              Output path. (default: "figure")
-t  <str> [str ...]     Markers will be added to the position corresponding to the timestamps here indicated.
-lp <word> [word ...]   Legend position (e.g. lower left, upper right). (default: lower left)
-mi <int>               Manual positioning of the markers on the map.
-bm [zoom]              Basemap zoom level. If omitted the background is white. If [zoom] is omitted: 15 (single day), 14 (multiday).
-v                      Verbose output.
-h                      Show this message and exit.
              """)
        return None

    # input path
    if "p" in args:
        if len(args["p"]) != 1:
            out["multiday"] = True
        out["path"] = args["p"]
    else:
        print("No input file")
        return -1

    # output path
    if "op" in args:
        if len(args["op"]) != 1:
            print("Too many output paths")
            return -1
        out["outpath"] = args["op"][0]
    else:
        out["outpath"] = ""

    # time strings
    if "t" in args:
        out["timestrings"] = args["t"]
    else:
        out["timestrings"] = []

    # verbose
    if "v" in args:
        out["verbose"] = True
    else:
        out["verbose"] = False

    # legend position: lower/upper left/right
    if "lp" in args:
        out["leg_pos"] = ""
        for w in args["lp"]:
            out["leg_pos"] += w
            out["leg_pos"] += " "
        out["leg_pos"] = leg_pos[:-1]
    else:
        out["leg_pos"] = "lower left"

    # manual addition of points on the track
    if "mi" in args:
        assert len(args["mi"]) == 1
        out["manual_img"] = int(args["mi"][0])
    else:
        out["manual_img"] = None

    # basemap
    if "bm" in args:
        if len(args["bm"]) == 1:
            out["basemap_zoom"] = int(args["bm"][0])
        elif len(args["bm"]) == 0:
            if out["multiday"]:
                out["basemap_zoom"] = 14
            else:
                out["basemap_zoom"] = 15
        else:
            print("Too many basemap zoom values")
            return -1
    else:
        out["basemap_zoom"] = None

    return out


def main():

    opt_dict = parse_cmdline()
    # in case of -h
    if opt_dict is None:
        return

    if not opt_dict["multiday"]:
        gpx = tl.GpxReadout(opt_dict["path"][0])
        pl.plottrack(gpx, **opt_dict)
        if gpx.numhr != 0:
            pl.plothr(gpx, **opt_dict)
        if gpx.numele != 0:
            pl.plotele(gpx, **opt_dict)

    else:
        gpxs = [tl.GpxReadout(p) for p in opt_dict["path"]]
        pl.plotmultiday(gpxs, **opt_dict)


if __name__ == "__main__":
    main()
