import io
import math
import asyncio
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from PIL import Image, ImageDraw, ImageFont
import mercantile
import os
import mgrs

app = FastAPI(title="MapGenerator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROVIDERS = {
    "osm": {
        "name": "OpenStreetMap",
        "url": "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
        "max_zoom": 19
    },
    "esri_satellite": {
        "name": "ESRI World Imagery",
        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "max_zoom": 19
    },
    "esri_topo": {
        "name": "ESRI World Topo",
        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        "max_zoom": 19
    },
    "carto_dark": {
        "name": "Carto Dark Matter",
        "url": "https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
        "max_zoom": 20
    },
    "carto_light": {
        "name": "Carto Positron",
        "url": "https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
        "max_zoom": 20
    },
    "opentopomap": {
        "name": "OpenTopoMap",
        "url": "https://a.tile.opentopomap.org/{z}/{x}/{y}.png",
        "max_zoom": 17
    },
    "esri_natgeo": {
        "name": "ESRI NatGeo",
        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}",
        "max_zoom": 16
    },
    "esri_street": {
        "name": "ESRI Street Map",
        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        "max_zoom": 19
    },
    "carto_voyager": {
        "name": "Carto Voyager (Bright)",
        "url": "https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png",
        "max_zoom": 20
    },
    "esri_hybrid": {
        "name": "ESRI Imagery Hybrid",
        "url": [
            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
        ],
        "max_zoom": 19
    },
    "esri_physical": {
        "name": "ESRI Physical Map",
        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}",
        "max_zoom": 8
    },
    "usgs_topo": {
        "name": "USGS Topo (US)",
        "url": "https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}",
        "max_zoom": 16
    },
    "usgs_imagery_topo": {
        "name": "USGS Imagery Hybrid (US)",
        "url": "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryTopo/MapServer/tile/{z}/{y}/{x}",
        "max_zoom": 16
    },
    "google_hybrid": {
        "name": "Google Hybrid Satellite",
        "url": "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        "max_zoom": 20
    },
    "google_streets": {
        "name": "Google Street Map",
        "url": "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        "max_zoom": 20
    },
    "google_terrain": {
        "name": "Google Terrain",
        "url": "https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
        "max_zoom": 20
    },
    "bing_satellite": {
        "name": "Bing Satellite",
        "url": "http://ecn.t3.tiles.virtualearth.net/tiles/a{q}.jpeg?g=1",
        "max_zoom": 19
    },
    "bing_streets": {
        "name": "Bing Streets",
        "url": "http://ecn.t3.tiles.virtualearth.net/tiles/r{q}.jpeg?g=1",
        "max_zoom": 19
    },
    "esri_light_gray": {
        "name": "ESRI Light Gray Canvas",
        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        "max_zoom": 16
    },
    "esri_dark_gray": {
        "name": "ESRI Dark Gray Canvas",
        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        "max_zoom": 16
    },
    "esri_terrain": {
        "name": "ESRI World Terrain",
        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}",
        "max_zoom": 13
    },
    "esri_ocean": {
        "name": "ESRI Ocean Basemap",
        "url": "https://server.arcgisonline.com/arcgis/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}",
        "max_zoom": 13
    },
    "esri_shaded_relief": {
        "name": "ESRI Shaded Relief",
        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}",
        "max_zoom": 13
    },
    "osm_hot": {
        "name": "OSM Humanitarian (HOT)",
        "url": "https://a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
        "max_zoom": 19
    },
    "cyclosm": {
        "name": "CyclOSM (Bicycle Map)",
        "url": "https://a.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png",
        "max_zoom": 20
    },
    "osm_fr": {
        "name": "OSM France (Clean OSM)",
        "url": "https://a.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png",
        "max_zoom": 20
    }
}

class MapRequest(BaseModel):
    west: float
    south: float
    east: float
    north: float
    width: int
    height: int
    provider: str
    constrain_aspect: bool = False
    pad_color: str = "#000000"
    show_scale: bool = False
    scale_unit: str = "metric"
    show_graticule: bool = False
    graticule_type: str = "latlon"

def tile_to_quadkey(x: int, y: int, z: int) -> str:
    quadkey = ""
    for i in range(z, 0, -1):
        digit = 0
        mask = 1 << (i - 1)
        if (x & mask) != 0:
            digit += 1
        if (y & mask) != 0:
            digit += 2
        quadkey += str(digit)
    return quadkey

async def fetch_tile(client: httpx.AsyncClient, url_template: str, x: int, y: int, z: int):
    if "{q}" in url_template:
        q = tile_to_quadkey(x, y, z)
        url = url_template.format(q=q)
    else:
        url = url_template.format(z=z, x=x, y=y)
    try:
        headers = {"User-Agent": "MapGenerator/1.0"}
        response = await client.get(url, headers=headers, timeout=15.0)
        response.raise_for_status()
        img = Image.open(io.BytesIO(response.content)).convert("RGBA")
        return (x, y, img)
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return (x, y, Image.new('RGBA', (256, 256), (0, 0, 0, 0)))

@app.get("/favicon.ico")
def favicon():
    return Response(content=b"", media_type="image/x-icon")

@app.get("/api/providers")
def get_providers():
    providers_list = [{"id": k, "name": v["name"]} for k, v in PROVIDERS.items()]
    return sorted(providers_list, key=lambda p: p['name'])

@app.post("/api/generate")
async def generate_map(req: MapRequest):
    if req.provider not in PROVIDERS:
        raise HTTPException(status_code=400, detail="Invalid provider")
        
    provider = PROVIDERS[req.provider]
    
    # Calculate mercator bounds
    w, s = mercantile.xy(req.west, req.south)
    e, n = mercantile.xy(req.east, req.north)
    bbox_m_width = e - w
    
    if bbox_m_width <= 0 or n - s <= 0:
        raise HTTPException(status_code=400, detail="Invalid bounding box")

    target_pixel_size = bbox_m_width / req.width
    # Calculate optimal zoom level based on requested target width
    # Resolution at zoom Z = 2 * pi * 6378137 / 256 / 2^Z
    earth_circumference = 2 * math.pi * 6378137.0
    try:
        calc_z = math.log2(earth_circumference / (256 * target_pixel_size))
        z = max(0, min(provider['max_zoom'], int(math.ceil(calc_z))))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid width/bounds calculation")

    tiles = list(mercantile.tiles(req.west, req.south, req.east, req.north, zooms=[z]))
    
    if len(tiles) > 400:
        raise HTTPException(status_code=400, detail="Requested resolution spans too many tiles. Try a smaller area or lower resolution.")
        
    min_x = min(t.x for t in tiles)
    max_x = max(t.x for t in tiles)
    min_y = min(t.y for t in tiles)
    max_y = max(t.y for t in tiles)
    
    canvas_w = (max_x - min_x + 1) * 256
    canvas_h = (max_y - min_y + 1) * 256
    canvas = Image.new('RGBA', (canvas_w, canvas_h), (255, 255, 255, 255))
    
    urls = provider["url"] if isinstance(provider["url"], list) else [provider["url"]]
    
    async with httpx.AsyncClient() as client:
        for url in urls:
            tasks = [fetch_tile(client, url, t.x, t.y, t.z) for t in tiles]
            results = await asyncio.gather(*tasks)
            
            for x, y, img in results:
                canvas.paste(img, ((x - min_x) * 256, (y - min_y) * 256), img)
                img.close()
        
    # Crop to exact bounding box
    canvas_tl = mercantile.xy_bounds(min_x, min_y, z)
    canvas_br = mercantile.xy_bounds(max_x, max_y, z)
    
    canvas_left = canvas_tl.left
    canvas_top = canvas_tl.top
    canvas_right = canvas_br.right
    
    resolution = (canvas_right - canvas_left) / canvas_w
    
    crop_left_px = (w - canvas_left) / resolution
    crop_top_px = (canvas_top - n) / resolution
    crop_right_px = (e - canvas_left) / resolution
    crop_bottom_px = (canvas_top - s) / resolution
    
    crop_box = (
        int(crop_left_px),
        int(crop_top_px),
        int(crop_right_px),
        int(crop_bottom_px)
    )
    
    final_img_cropped = canvas.crop(crop_box).convert("RGB")
    
    # Scale to requested width/height
    if req.constrain_aspect:
        final_img = final_img_cropped.resize((req.width, req.height), Image.Resampling.LANCZOS)
    else:
        aspect_ratio = final_img_cropped.height / final_img_cropped.width
        target_ratio = req.height / req.width
        
        if aspect_ratio > target_ratio:
            new_h = req.height
            new_w = int(req.height / aspect_ratio)
        else:
            new_w = req.width
            new_h = int(req.width * aspect_ratio)
            
        resized_map = final_img_cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Parse hex color
        try:
            pad_rgb = tuple(int(req.pad_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            pad_rgb = (0, 0, 0)
            
        final_img = Image.new('RGB', (req.width, req.height), pad_rgb)
        paste_x = (req.width - new_w) // 2
        paste_y = (req.height - new_h) // 2
        final_img.paste(resized_map, (paste_x, paste_y))
        
    # Apply Overlays
    if req.show_scale or req.show_graticule:
        # Convert to RGBA to properly blend transparent drawings
        final_img = final_img.convert("RGBA")
        overlay_layer = Image.new('RGBA', final_img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay_layer)
        
        try:
            # Try to load a nice font, fallback to default
            font = ImageFont.truetype("arial.ttf", 16)
            font_scale = ImageFont.truetype("arial.ttf", 14)
        except IOError:
            font = ImageFont.load_default()
            font_scale = font
            
        if req.constrain_aspect:
            map_px_x = 0
            map_px_y = 0
            map_px_w = req.width
            map_px_h = req.height
        else:
            map_px_x = paste_x
            map_px_y = paste_y
            map_px_w = new_w
            map_px_h = new_h
            
        def latlon_to_pixel(lon, lat):
            mx, my = mercantile.xy(lon, lat)
            fx = (mx - w) / (e - w) if e != w else 0.5
            fy = (n - my) / (n - s) if n != s else 0.5
            px_x = map_px_x + fx * map_px_w
            px_y = map_px_y + fy * map_px_h
            return int(px_x), int(px_y)
            
        def draw_dashed_line(pt1, pt2, fill, width, dash_len=8):
            x1, y1 = pt1
            x2, y2 = pt2
            dist = math.hypot(x2 - x1, y2 - y1)
            if dist == 0: return
            dx = (x2 - x1) / dist * dash_len
            dy = (y2 - y1) / dist * dash_len
            dashes = int(dist / dash_len)
            for i in range(dashes):
                if i % 2 == 0:
                    p1 = (x1 + i * dx, y1 + i * dy)
                    p2 = (x1 + (i + 1) * dx, y1 + (i + 1) * dy)
                    draw.line([p1, p2], fill=fill, width=width)
                    
        def draw_outlined_text(pos, text, font, text_fill, outline_fill):
            x, y = pos
            for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1), (0,-1), (-1,0), (1,0), (0,1)]:
                draw.text((x + dx, y + dy), text, fill=outline_fill, font=font)
            draw.text((x, y), text, fill=text_fill, font=font)
            
        def draw_graticule_line(pt1, pt2, color=(255,255,255,180), shadow=(0,0,0,150)):
            p1_s = (pt1[0] + 1, pt1[1] + 1)
            p2_s = (pt2[0] + 1, pt2[1] + 1)
            draw_dashed_line(p1_s, p2_s, fill=shadow, width=1, dash_len=10)
            draw_dashed_line(pt1, pt2, fill=color, width=1, dash_len=10)
            
        # Calculate true lat/lon bounds of the entire image including padding
        fx_min = -map_px_x / map_px_w if map_px_w != 0 else 0
        fx_max = (req.width - map_px_x) / map_px_w if map_px_w != 0 else 1
        mx_min = w + fx_min * (e - w)
        mx_max = w + fx_max * (e - w)
        
        fy_min = -map_px_y / map_px_h if map_px_h != 0 else 0
        fy_max = (req.height - map_px_y) / map_px_h if map_px_h != 0 else 1
        my_max = n - fy_min * (n - s)
        my_min = n - fy_max * (n - s)
        
        lng_min, lat_min = mercantile.lnglat(mx_min, my_min)
        lng_max, lat_max = mercantile.lnglat(mx_max, my_max)
            
        if req.show_graticule:
            if req.graticule_type == "mgrs":
                m = mgrs.MGRS()
                center_lat = (req.south + req.north) / 2.0
                center_lon = (req.west + req.east) / 2.0
                try:
                    c_mgrs = m.toMGRS(center_lat, center_lon)
                    z, h, e_c, n_c = m.MGRSToUTM(c_mgrs)
                    
                    total_height_meters = (n - s) * (req.height / map_px_h) if map_px_h != 0 else (n - s)
                    total_width_meters = (e - w) * (req.width / map_px_w) if map_px_w != 0 else (e - w)
                    
                    min_e = e_c - total_width_meters * 0.8
                    max_e = e_c + total_width_meters * 0.8
                    min_n = n_c - total_height_meters * 0.8
                    max_n = n_c + total_height_meters * 0.8
                    
                    span_e = max_e - min_e
                    if span_e > 100000: interval = 100000
                    elif span_e > 10000: interval = 10000
                    elif span_e > 5000: interval = 1000
                    else: interval = 100
                    
                    start_e = math.ceil(min_e / interval) * interval
                    start_n = math.ceil(min_n / interval) * interval
                    
                    curr_e = start_e
                    while curr_e <= max_e:
                        try:
                            lat_s, lon_s = m.toLatLon(m.UTMToMGRS(z, h, curr_e, min_n))
                            lat_n, lon_n = m.toLatLon(m.UTMToMGRS(z, h, curr_e, max_n))
                            px1 = latlon_to_pixel(lon_s, lat_s)
                            px2 = latlon_to_pixel(lon_n, lat_n)
                            draw_graticule_line(px1, px2)
                            label = f"{int(curr_e)}"
                            draw_outlined_text((px1[0] + 5, px1[1] - 20), label, font, (255,255,255,220), (0,0,0,180))
                        except Exception:
                            pass
                        curr_e += interval
                        
                    curr_n = start_n
                    while curr_n <= max_n:
                        try:
                            lat_w, lon_w = m.toLatLon(m.UTMToMGRS(z, h, min_e, curr_n))
                            lat_e, lon_e = m.toLatLon(m.UTMToMGRS(z, h, max_e, curr_n))
                            px1 = latlon_to_pixel(lon_w, lat_w)
                            px2 = latlon_to_pixel(lon_e, lat_e)
                            draw_graticule_line(px1, px2)
                            label = f"{int(curr_n)}"
                            draw_outlined_text((px1[0] + 5, px1[1] + 5), label, font, (255,255,255,220), (0,0,0,180))
                        except Exception:
                            pass
                        curr_n += interval
                except Exception as e:
                    print(f"MGRS overlay error: {e}")
            else:
                lat_span = lat_max - lat_min
                if lat_span > 10: interval = 5.0
                elif lat_span > 2: interval = 1.0
                elif lat_span > 0.5: interval = 0.1
                elif lat_span > 0.1: interval = 0.05
                else: interval = 0.01
                
                start_lat = math.ceil(lat_min / interval) * interval
                start_lon = math.ceil(lng_min / interval) * interval
                
                lat = start_lat
                while lat <= lat_max:
                    px1 = latlon_to_pixel(lng_min, lat)
                    px2 = latlon_to_pixel(lng_max, lat)
                    draw_graticule_line(px1, px2)
                    label = f"{lat:.3f}°"
                    draw_outlined_text((px1[0] + 10, px1[1] - 20), label, font, (255,255,255,220), (0,0,0,180))
                    lat += interval
                    
                lon = start_lon
                while lon <= lng_max:
                    px1 = latlon_to_pixel(lon, lat_min)
                    px2 = latlon_to_pixel(lon, lat_max)
                    draw_graticule_line(px1, px2)
                    label = f"{lon:.3f}°"
                    draw_outlined_text((px2[0] + 10, px2[1] + 10), label, font, (255,255,255,220), (0,0,0,180))
                    lon += interval

        if req.show_scale:
            center_lat = (req.north + req.south) / 2.0
            earth_circumference = 2 * math.pi * 6378137.0
            meters_per_lon_degree = earth_circumference * math.cos(math.radians(center_lat)) / 360.0
            total_width_meters = (req.east - req.west) * meters_per_lon_degree
            meters_per_pixel = total_width_meters / map_px_w
            
            def get_nice_val(target):
                if target <= 0: return 1
                mag = 10 ** math.floor(math.log10(target))
                norm = target / mag
                if norm < 2: nice = 1
                elif norm < 5: nice = 2
                elif norm < 8: nice = 5
                else: nice = 10
                return nice * mag
                
            target_pixels = min(req.width * 0.15, 250)
            if req.scale_unit == "imperial":
                target_feet = target_pixels * meters_per_pixel * 3.28084
                if target_feet > 5280 / 2:
                    nice_mi = get_nice_val(target_feet / 5280)
                    label = f"{int(nice_mi) if nice_mi.is_integer() else nice_mi} mi"
                    bar_len_px = (nice_mi * 5280 / 3.28084) / meters_per_pixel
                else:
                    nice_ft = get_nice_val(target_feet)
                    label = f"{int(nice_ft)} ft"
                    bar_len_px = (nice_ft / 3.28084) / meters_per_pixel
            elif req.scale_unit == "nautical":
                target_nm = target_pixels * meters_per_pixel / 1852.0
                nice_nm = get_nice_val(target_nm)
                label = f"{int(nice_nm) if nice_nm.is_integer() else nice_nm} nm"
                bar_len_px = (nice_nm * 1852.0) / meters_per_pixel
            else:
                target_m = target_pixels * meters_per_pixel
                if target_m > 1000:
                    nice_km = get_nice_val(target_m / 1000)
                    label = f"{int(nice_km) if nice_km.is_integer() else nice_km} km"
                    bar_len_px = (nice_km * 1000) / meters_per_pixel
                else:
                    nice_m = get_nice_val(target_m)
                    label = f"{int(nice_m)} m"
                    bar_len_px = nice_m / meters_per_pixel
                    
            bbox = draw.textbbox((0, 0), label, font=font_scale)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            
            padding_right = max(40, int(tw / 2) + 20)
            sx2 = req.width - padding_right
            sx1 = sx2 - bar_len_px
            sy1 = req.height - 40 - 20
            
            box_top = sy1 - th - 12
            box_bottom = sy1 + 10
            draw.rectangle([sx1-15, box_top, sx2+15, box_bottom], fill=(255, 255, 255, 200), outline=(0,0,0,50))
            
            # Main border
            draw.rectangle([sx1, sy1, sx2, sy1 + 6], fill=(255, 255, 255, 255), outline=(0,0,0,255))
            
            # Fill half with black
            mid_x = sx1 + bar_len_px / 2.0
            draw.rectangle([sx1, sy1, mid_x, sy1 + 6], fill=(0, 0, 0, 255))
            
            # Ticks
            draw.line([(sx1, sy1-4), (sx1, sy1)], fill=(0,0,0,255), width=1)
            draw.line([(mid_x, sy1-4), (mid_x, sy1)], fill=(0,0,0,255), width=1)
            draw.line([(sx2, sy1-4), (sx2, sy1)], fill=(0,0,0,255), width=1)
            
            # Text
            text_y = sy1 - th - 8
            draw.text((sx2 - tw/2, text_y), label, fill=(0,0,0,255), font=font_scale)
            draw.text((sx1 - 4, text_y), "0", fill=(0,0,0,255), font=font_scale)

        final_img = Image.alpha_composite(final_img, overlay_layer).convert("RGB")

    img_byte_arr = io.BytesIO()
    final_img.save(img_byte_arr, format='JPEG', quality=95)
    img_byte_arr.seek(0)
    
    return StreamingResponse(img_byte_arr, media_type="image/jpeg", headers={
        "Content-Disposition": f"attachment; filename=map_{req.width}px.jpg"
    })

os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
