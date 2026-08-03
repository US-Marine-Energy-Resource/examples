"""PacWave corner provenance and folium map helpers.

The notebook holds the assessment coordinates it works from; this module keeps
the two things that are not bare lat/lon pairs: the published PacWave corner
coordinates (and their sources), from which the berth centerpoints are computed,
and the folium map builders the notebook renders through.
"""

import html

import folium
import numpy as np


def centerpoint(corners):
    return {
        "lat": float(np.mean([corner["lat"] for corner in corners.values()])),
        "lng": float(np.mean([corner["lng"] for corner in corners.values()])),
    }


# PacWave points, keyed by name. Each keeps its published corner coordinates and
# computes its berth centerpoint (lat/lng) from them. Every other assessment
# coordinate lives in the notebook (the POINTS dict), not here.
PACWAVE_POINTS = {
    # https://oregonstate.app.box.com/s/w9akpvhpev03mv4sqotl0vzm2dgk5xdq
    # PACWAVE SOUTH WAVE ENERGY
    # TEST SITE Testing Wave Energy for the Future
    # PacWave is an open ocean, wave energy testing facility at Oregon State University. It consists
    # of two sites, each located within several miles of the deep water commercial port of Newport,
    # Oregon. PacWave South is an in-development, state-of-the-art, pre-permitted, accredited,
    # grid- connected wave energy test facility; developed in partnership with the US Department of
    # Energy, the State of Oregon and local stakeholders. Construction started in 2021 and will be
    # completed in 2024, with testing starting in 2025.
    # SITE SPECIFICATIONS
    # • Number of berths: 4
    # • Location of Test Site: 6 nautical miles off the coast of Newport Oregon
    # • Depth of site: 65-78 meters MLLW
    # • Site coordinates:
    # NW: 44º 35' 00.00"N 124º 14' 30.00"W
    # NE: 44º 35' 02.75"N 124º 13' 06.17"W
    # SE: 44º 33' 02.75"N 124º 12' 58.51"W
    # SW: 44º 33' 00.00"N 124º 14' 22.41"W
    # • Nature of seabed: Soft, sandy bottom
    # • Wave data facilities: Waverider buoys, Spotter buoys, or similar
    # • Mean annual wave power density: 40 kW/m, varies with year and location
    # • Wave periods: 5-17s
    # • Prevailing wave direction: WNW
    # • Sea states: The majority of sea states are within the range of:
    # 1m < Hm0 < 3.5m and 7s < Te < 11s,
    # including extreme sea states caused by severe storms where Hm0 exceeded 7.5m.
    # • Environmental site characterization data
    # • Meteorological data
    # • Technical capacity: data acquisition, rated export capacity of berths:
    # 20MW Connection Voltage: 12.47kV to CLPUD, berths configurable up to 30kV
    # • Site access nearest port: Newport and Toledo portofnewport.com portoftoledo.org
    # • Support Facilities: Berthing & working areas, office facilities, boatyard
    # • Grid Connection: Metered at point of connection to the Central Lincoln People's Utility Distric
    "US_Oregon_PacWave_South": {
        "label": "PacWave South",
        "color": "steelblue",
        "corners": {
            # NW: 44º 35' 00.00"N 124º 14' 30.00"W
            # https://www.google.com/maps/place/44%C2%B035'00.0%22N+124%C2%B014'30.0%22W/@44.5833333,-124.2416667,1231m/data=!3m2!1e3!4b1!4m4!3m3!8m2!3d44.5833333!4d-124.2416667?entry=ttu&g_ep=EgoyMDI2MDcxMi4wIKXMDSoASAFQAw%3D%3D
            "Northwest Corner": {"lat": 44.583333, "lng": -124.241667},
            # NE: 44º 35' 02.75"N 124º 13' 06.17"W
            # https://www.google.com/maps/place/44%C2%B035'02.8%22N+124%C2%B013'06.2%22W/@44.5840972,-124.2183806,1231m/data=!3m2!1e3!4b1!4m4!3m3!8m2!3d44.5840972!4d-124.2183806?entry=ttu&g_ep=EgoyMDI2MDcxMi4wIKXMDSoASAFQAw%3D%3D
            # Northeast Corner: (44.584097, -124.218381)
            "Northeast Corner": {"lat": 44.584097, "lng": -124.218381},
            # SW: 44º 33' 00.00"N 124º 14' 22.41"W
            # https://www.google.com/maps/place/44%C2%B033'00.0%22N+124%C2%B014'22.4%22W/@44.5507677,-124.2188277,1232m/data=!3m1!1e3!4m4!3m3!8m2!3d44.55!4d-124.2395583?entry=ttu&g_ep=EgoyMDI2MDcxMi4wIKXMDSoASAFQAw%3D%3D
            "Southwest Corner": {"lat": 44.550764, "lng": -124.216253},
            # SE: 44º 33' 02.75"N 124º 12' 58.51"W
            # https://www.google.com/maps/place/44%C2%B033'02.8%22N+124%C2%B012'58.5%22W/@44.5507677,-124.2188277,1232m/data=!3m2!1e3!4b1!4m4!3m3!8m2!3d44.5507639!4d-124.2162528?entry=ttu&g_ep=EgoyMDI2MDcxMi4wIKXMDSoASAFQAw%3D%3D
            "Southeast Corner": {"lat": 44.550000, "lng": -124.239558},
        },
    },
    # PACWAVE NORTH WAVE ENERGY
    # TEST SITE
    # SITE SPECIFICATIONS
    # Testing Wave Energy for the Future
    # PacWave is an open ocean wave energy testing facility at Oregon State University. It consists
    # of two sites, each located within several miles of the deep-water commercial port of Newport,
    # Oregon. PacWave North is an established autonomous test site for small-scale, prototype, and
    # maritime market technologies. PacWave North offers a site in state waters with streamlined
    # permitting; expected time to permit is under one year. The site is shallower than PacWave
    # South and closer to port. PacWave North is a persistently monitored site (wave, metocean
    # measurements, and habitat surveys).
    # • Flexible number of berths
    # • Located 2 nautical miles off the coastline
    # • Depth is 45-55 meters MLLW
    # • Site Coordinates:
    # NW: 44º 41' 52.08"N 124º 08' 46.32"W
    # NE: 44º 41' 54.96"N 124º 07' 22.44"W
    # SE: 44º 40' 54.84"N 124º 07' 18.48"W
    # SW: 44º 40' 52.32"N 124º 08' 42.72"W
    # • Seabed has a soft, sandy bottom
    # • Mean annual wave power density is 40kW/m,
    # variable with year/location
    # • Wave data facilities include Waverider
    # or similar buoys
    # • Wave periods are 5-17s
    # • Prevailing Wave Direction is WNW
    # • The majority of sea states are within the
    # range of:
    # 1m < H m0 < 3.5m and 7s < T e < 11s @ wvw
    # including extreme sea states caused by
    # severe storms where H m0 exceeded 7.5m
    "US_Oregon_PacWave_North": {
        "label": "PacWave North",
        "color": "#d62728",
        "corners": {
            # NW: 44º 41' 52.08"N 124º 08' 46.32"W
            # https://www.google.com/maps/place/44%C2%B041'52.1%22N+124%C2%B008'46.3%22W/@44.6978038,-124.1487749,1229m/data=!3m2!1e3!4b1!4m4!3m3!8m2!3d44.6978!4d-124.1462?entry=ttu&g_ep=EgoyMDI2MDcxMi4wIKXMDSoASAFQAw%3D%3D
            # Northwest Corner: (44.697800, -124.146200)
            "Northwest Corner": {"lat": 44.697800, "lng": -124.146200},
            # NE: 44º 41' 54.96"N 124º 07' 22.44"W
            # https://www.google.com/maps/place/44%C2%B041'55.0%22N+124%C2%B007'22.4%22W/@44.6978038,-124.1487749,1229m/data=!3m1!1e3!4m4!3m3!8m2!3d44.6986!4d-124.1229?entry=ttu&g_ep=EgoyMDI2MDcxMi4wIKXMDSoASAFQAw%3D%3D
            # Northeast Corner: (44.698600, -124.122900)
            "Northeast Corner": {"lat": 44.698600, "lng": -124.122900},
            # SE: 44º 40' 54.84"N 124º 07' 18.48"W
            # https://www.google.com/maps/search/44%C2%BA+40%E2%80%99+54.84%E2%80%9DN+124%C2%BA+07%E2%80%99+18.48%E2%80%9DW/@44.6986038,-124.1254749,1229m/data=!3m1!1e3?entry=ttu&g_ep=EgoyMDI2MDcxMi4wIKXMDSoASAFQAw%3D%3D
            # Southeast Corner: (44.681900, -124.121800)
            "Southeast Corner": {"lat": 44.681900, "lng": -124.121800},
            # SW: 44º 40' 52.32"N 124º 08' 42.72"W
            # https://www.google.com/maps/place/44%C2%B040'52.3%22N+124%C2%B008'42.7%22W/@44.6812038,-124.1477749,1229m/data=!3m2!1e3!4b1!4m4!3m3!8m2!3d44.6812!4d-124.1452?entry=ttu&g_ep=EgoyMDI2MDcxMi4wIKXMDSoASAFQAw%3D%3D
            # Southwest Corner: (44.681200, -124.145200)
            "Southwest Corner": {"lat": 44.681200, "lng": -124.145200},
        },
    },
}

for _point in PACWAVE_POINTS.values():
    if "corners" in _point:
        _point.update(centerpoint(_point["corners"]))


def point_coord(point):
    return (point["lat"], point["lng"])


def ordered_corners(corners):
    ordered = sorted(corners.values(), key=lambda corner: corner["lat"], reverse=True)
    north = sorted(ordered[:2], key=lambda corner: corner["lng"])
    south = sorted(ordered[2:], key=lambda corner: corner["lng"], reverse=True)
    return [*north, *south]


def make_points_map(points):
    center = [
        np.mean([point["lat"] for point in points.values()]),
        np.mean([point["lng"] for point in points.values()]),
    ]
    point_map = folium.Map(location=center, zoom_start=4)

    for point in points.values():
        if "corners" in point:
            add_point_bounds(point_map, point)

    for point in points.values():
        folium.Marker(
            location=[point["lat"], point["lng"]],
            tooltip=point["label"],
        ).add_to(point_map)
        add_point_label(point_map, point)
    return point_map


def add_point_label(point_map, point):
    label = html.escape(point["label"])
    folium.Marker(
        location=[point["lat"], point["lng"]],
        icon=folium.DivIcon(
            icon_size=(150, 24),
            icon_anchor=(-8, 18),
            class_name="point-label",
            html=f"""
            <div style="
                color: #111827;
                font-size: 12px;
                font-weight: 600;
                line-height: 1.2;
                white-space: nowrap;
                text-shadow: -1px -1px 0 white, 1px -1px 0 white,
                             -1px 1px 0 white, 1px 1px 0 white;
                pointer-events: none;
            ">{label}</div>
            """,
        ),
    ).add_to(point_map)


def add_point_bounds(point_map, point):
    color = point["color"]
    bounds = [
        [corner["lat"], corner["lng"]] for corner in ordered_corners(point["corners"])
    ]
    folium.Polygon(
        locations=bounds,
        color=color,
        weight=2,
        fill=True,
        fill_color=color,
        fill_opacity=0.18,
        tooltip=folium.Tooltip(point["label"], permanent=False),
    ).add_to(point_map)
