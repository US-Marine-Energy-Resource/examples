"""Wave energy test sites: coordinates, provenance, and map/link helpers.

Everything about the sites that is not a bare lat/lon pair lives here -- the
published PacWave corner coordinates and their sources, the folium map builders,
and the Marine Energy Atlas deep links -- so the notebook can present a clean
name/coordinate table and leave the bookkeeping to this module.
"""

import html
import json

from urllib.parse import urlencode

import folium
import numpy as np


def centerpoint(corners):
    return {
        "lat": float(np.mean([corner["lat"] for corner in corners.values()])),
        "lng": float(np.mean([corner["lng"] for corner in corners.values()])),
    }


# Sites keyed by name -> {"lat": latitude, "lng": longitude, "label": short label}.
# PacWave sites also retain their original corners and calculate lat/lng from them.
WAVE_ENERGY_TEST_SITES = {
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
    # Azura Deployment Site: https://en.wikipedia.org/wiki/Azura_(wave_power_device)
    "US_Hawaii_Oahu_WETS": {
        "lat": 21.46488,
        "lng": -157.751524,
        "label": "WETS",
    },
    # HERO WEC: https://modaq.nlr.gov/hero-wec-dashboard/?tab=location
    "US_North_Carolina_Jenettes_Pier": {
        "lat": 35.91036,
        "lng": -75.59239,
        "label": "Jennette's Pier",
    },
    # https://tethys-engineering.pnnl.gov/sites/default/files/publications/Coe-et-al-2023.pdf
    # NOTE: the key says Massachusetts but these coordinates are ~60 km off the
    # North Carolina coast, so this site sits in the Atlantic domain either way.
    "US_Massachusetts_WoodsHole_PioneerWec": {
        "lat": 35.943117,
        "lng": -74.88035,
        "label": "Pioneer WEC",
    },
    # CalWave Deployment: https://mhkdr.openei.org/files/322/CalWave_IOM_Revised.pdf
    "US_California_Scripps_Pier": {
        "lat": 32.867633,
        "lng": -117.263167,
        "label": "Scripps Pier",
    },
    # Best Guess
    # https://www.google.com/maps/@35.163837,-120.7279724,5653m/data=!3m1!1e3?entry=ttu&g_ep=EgoyMDI2MDcxMi4wIKXMDSoASAFQAw%3D%3D
    "US_California_San_Luis_Obispo": {
        "lat": 35.1672960606959,
        "lng": -120.740349224586,
        "label": "San Luis Obispo",
    },
    # Humboldt Bay, CA. Coordinates taken from the DOE-WPTO US Wave dataset viewer,
    # which reports this as location ID 596791: water depth 48 m, 5344.78 m to shore.
    # The wave_hindcast node lookup independently resolves the same node -- gid
    # 596791 -- which is a useful end-to-end check of the site lookup against an
    # authority outside this repository. (The viewer lists its time zone as 0; the
    # file itself says -8, with jurisdiction "California".)
    "US_California_Humboldt_Bay": {
        "lat": 40.8398,
        "lng": -124.25,
        "label": "Humboldt Bay",
    },
    # The two sites below carry no test facility; they are open-water points chosen
    # to exercise the Alaska and Gulf of Mexico / Puerto Rico domains, which no
    # site above reaches.
    "US_Alaska_Kodiak": {
        "lat": 57.0,
        "lng": -152.5,
        "label": "Kodiak (open water)",
    },
    "US_PuertoRico_North_Shore": {
        "lat": 18.60,
        "lng": -66.10,
        "label": "N. of San Juan (open water)",
    },
}

for _site in WAVE_ENERGY_TEST_SITES.values():
    if "corners" in _site:
        _site.update(centerpoint(_site["corners"]))


def site_lat_lng(site):
    return (site["lat"], site["lng"])


def ordered_corners(corners):
    ordered = sorted(corners.values(), key=lambda corner: corner["lat"], reverse=True)
    north = sorted(ordered[:2], key=lambda corner: corner["lng"])
    south = sorted(ordered[2:], key=lambda corner: corner["lng"], reverse=True)
    return [*north, *south]


def make_sites_map(sites):
    center = [
        np.mean([site["lat"] for site in sites.values()]),
        np.mean([site["lng"] for site in sites.values()]),
    ]
    site_map = folium.Map(location=center, zoom_start=4)

    for site in sites.values():
        if "corners" in site:
            add_site_bounds(site_map, site)

    for site in sites.values():
        folium.Marker(
            location=[site["lat"], site["lng"]],
            tooltip=site["label"],
        ).add_to(site_map)
        add_site_label(site_map, site)
    return site_map


def add_site_label(site_map, site):
    label = html.escape(site["label"])
    folium.Marker(
        location=[site["lat"], site["lng"]],
        icon=folium.DivIcon(
            icon_size=(150, 24),
            icon_anchor=(-8, 18),
            class_name="site-label",
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
    ).add_to(site_map)


def add_site_bounds(site_map, site):
    color = site["color"]
    bounds = [
        [corner["lat"], corner["lng"]] for corner in ordered_corners(site["corners"])
    ]
    folium.Polygon(
        locations=bounds,
        color=color,
        weight=2,
        fill=True,
        fill_color=color,
        fill_opacity=0.18,
        tooltip=folium.Tooltip(site["label"], permanent=False),
    ).add_to(site_map)


# NREL Marine Energy Atlas deep links. The viewer's URL carries no per-point
# parameter -- clicking a marker only rewrites the `b` viewport bounds -- so the
# best available link is a bounding box drawn tightly around the site, which opens
# the map zoomed onto it. `vL` selects the displayed layer and is copied from the
# viewer; change it to link against a different layer.
ATLAS_URL = "https://maps.nrel.gov/marine-energy-atlas/data-viewer/data-library/layers"
ATLAS_LAYER = "68c955d8b12e9eb9d3c3fc55"
# Half-extents of the framing box, in degrees. ~2.2:1 to match the viewer's aspect.
ATLAS_HALF_LAT, ATLAS_HALF_LNG = 0.045, 0.10


def atlas_url(site, layer=ATLAS_LAYER):
    bounds = [
        [round(site["lng"] - ATLAS_HALF_LNG, 6), round(site["lat"] - ATLAS_HALF_LAT, 6)],
        [round(site["lng"] + ATLAS_HALF_LNG, 6), round(site["lat"] + ATLAS_HALF_LAT, 6)],
    ]
    query = urlencode({"vL": layer, "b": json.dumps(bounds, separators=(",", ":"))})
    return f"{ATLAS_URL}?{query}"
