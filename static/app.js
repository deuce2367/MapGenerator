document.addEventListener('DOMContentLoaded', async () => {
    // 1. App State
    let map;
    let baseLayer;
    let currentProviderId = 'carto_dark';
    let drawnItems;
    let currentBounds = null; // {west, south, east, north}
    
    // 2. DOM Elements
    const providerSelect = document.getElementById('provider');
    const resolutionSelect = document.getElementById('resolution');
    const generateBtn = document.getElementById('generate-btn');
    const btnText = generateBtn.querySelector('span');
    const loader = document.getElementById('loader');
    const errorMsg = document.getElementById('error-msg');

    // 3. Initialize Map
    function initMap() {
        map = L.map('map').setView([48.8566, 2.3522], 12); // Paris default
        
        drawnItems = new L.FeatureGroup();
        map.addLayer(drawnItems);
        
        const drawControl = new L.Control.Draw({
            draw: {
                polyline: false,
                polygon: false,
                circle: false,
                marker: false,
                circlemarker: false,
                rectangle: {
                    shapeOptions: {
                        color: '#3b82f6',
                        weight: 2,
                        fillOpacity: 0.1
                    }
                }
            },
            edit: {
                featureGroup: drawnItems
            }
        });
        map.addControl(drawControl);

    // Helper to snap rectangle to 16:9
    function enforceBoundsRatio(layer) {
        if (!document.getElementById('constrain-ratio').checked) return;
        
        const bounds = layer.getBounds();
        const center = bounds.getCenter();
        
        // Approximate pixel-level lengths to keep aspect ratio sensible geographically
        const pnw = map.project(bounds.getNorthWest(), 10);
        const pse = map.project(bounds.getSouthEast(), 10);
        
        let pw = Math.abs(pse.x - pnw.x);
        let ph = Math.abs(pse.y - pnw.y);
        if (pw === 0 || ph === 0) return;
        
        const targetRatio = 16 / 9;
        const currentRatio = pw / ph;
        
        if (currentRatio < targetRatio) {
            // Expand width
            pw = ph * targetRatio;
        } else {
            // Expand height
            ph = pw / targetRatio;
        }
        
        const pCenter = map.project(center, 10);
        const newNw = map.unproject([pCenter.x - pw/2, pCenter.y - ph/2], 10);
        const newSe = map.unproject([pCenter.x + pw/2, pCenter.y + ph/2], 10);
        
        layer.setBounds(L.latLngBounds(newNw, newSe));
    }

    // Handle Map Draw Events
    map.on(L.Draw.Event.CREATED, function (e) {
        drawnItems.clearLayers(); // Only allow one box
        const layer = e.layer;
        
        enforceBoundsRatio(layer);
        
        drawnItems.addLayer(layer);
        
        const bounds = layer.getBounds();
        currentBounds = {
            west: bounds.getWest(),
            south: bounds.getSouth(),
            east: bounds.getEast(),
            north: bounds.getNorth()
        };
        
        generateBtn.disabled = false;
        errorMsg.textContent = "";
    });

    map.on(L.Draw.Event.DELETED, function() {
            currentBounds = null;
            generateBtn.disabled = true;
        });
        
        map.on(L.Draw.Event.EDITED, function(e) {
            const layers = e.layers;
            layers.eachLayer(function (layer) {
                enforceBoundsRatio(layer);
                const bounds = layer.getBounds();
                currentBounds = {
                    west: bounds.getWest(),
                    south: bounds.getSouth(),
                    east: bounds.getEast(),
                    north: bounds.getNorth()
                };
            });
        });
    }

    // Toggle Padding UI & Constraint Watcher
    const constrainCheckbox = document.getElementById('constrain-ratio');
    const paddingGroup = document.getElementById('padding-color-group');

    function togglePaddingUI() {
        if (constrainCheckbox.checked) {
            paddingGroup.style.display = 'none';
        } else {
            paddingGroup.style.display = 'block';
        }
    }

    constrainCheckbox.addEventListener('change', () => {
        togglePaddingUI();
        if (constrainCheckbox.checked && drawnItems.getLayers().length > 0) {
            const layer = drawnItems.getLayers()[0];
            enforceBoundsRatio(layer);
            const bounds = layer.getBounds();
            currentBounds = {
                west: bounds.getWest(),
                south: bounds.getSouth(),
                east: bounds.getEast(),
                north: bounds.getNorth()
            };
        }
    });

    togglePaddingUI();

    // 4. Fetch Providers from Backend
    async function loadProviders() {
        try {
            const res = await fetch('/api/providers');
            if (!res.ok) throw new Error('Failed to fetch providers');
            const providers = await res.json();
            
            providers.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.id;
                opt.textContent = p.name;
                providerSelect.appendChild(opt);
            });
            providerSelect.value = currentProviderId;
            updateBaseLayer();
        } catch (e) {
            errorMsg.textContent = "Could not reach backend to load map providers.";
            console.error(e);
        }
    }

    // 5. Update Leaflet Base Layer based on Selection
    function updateBaseLayer() {
        currentProviderId = providerSelect.value;
        
        // This is a rough client-side mapping for preview purposes.
        // The real stitching happens backend. We construct standard XYZ urls for preview.
        let url = '';
        if(currentProviderId === 'osm') url = 'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png';
        if(currentProviderId === 'esri_satellite') url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
        if(currentProviderId === 'esri_topo') url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}';
        if(currentProviderId === 'carto_dark') url = 'https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png';
        if(currentProviderId === 'carto_light') url = 'https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png';
        if(currentProviderId === 'opentopomap') url = 'https://a.tile.opentopomap.org/{z}/{x}/{y}.png';
        if(currentProviderId === 'osm_hot') url = 'https://a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png';
        if(currentProviderId === 'cyclosm') url = 'https://a.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png';
        if(currentProviderId === 'osm_fr') url = 'https://a.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png';
        if(currentProviderId === 'esri_natgeo') url = 'https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}';
        if(currentProviderId === 'esri_street') url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}';
        if(currentProviderId === 'carto_voyager') url = 'https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png';
        if(currentProviderId === 'esri_physical') url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}';
        if(currentProviderId === 'usgs_topo') url = 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}';
        if(currentProviderId === 'usgs_imagery_topo') url = 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryTopo/MapServer/tile/{z}/{y}/{x}';
        if(currentProviderId === 'google_hybrid') url = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}';
        if(currentProviderId === 'google_streets') url = 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}';
        if(currentProviderId === 'google_terrain') url = 'https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}';
        
        // Leaflet doesn't natively support quadkeys easily without a plugin. 
        // For Bing previews, we'll construct a simple approximation or just fallback to OSM if quadkey fails.
        // Actually, since this is just a rough preview, we can leave Bing URLs blank or implement a quick custom layer if needed.
        // To keep it simple, we'll map Bing to Google for preview, but real generation uses Bing.
        if(currentProviderId === 'bing_satellite') url = 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}';
        if(currentProviderId === 'bing_streets') url = 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}';
        
        if(currentProviderId === 'esri_light_gray') url = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}';
        if(currentProviderId === 'esri_dark_gray') url = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}';
        if(currentProviderId === 'esri_terrain') url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}';
        if(currentProviderId === 'esri_ocean') url = 'https://server.arcgisonline.com/arcgis/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}';
        if(currentProviderId === 'esri_shaded_relief') url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}';

        if (baseLayer) {
            map.removeLayer(baseLayer);
        }
        
        if (currentProviderId === 'esri_hybrid') {
            const base = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19 });
            const ref = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19 });
            baseLayer = L.layerGroup([base, ref]).addTo(map);
        } else {
            baseLayer = L.tileLayer(url, { maxZoom: 19 }).addTo(map);
        }
    }

    providerSelect.addEventListener('change', updateBaseLayer);

    // 6. Generate Map Action
    generateBtn.addEventListener('click', async () => {
        if (!currentBounds) return;

        // UI Loading State
        generateBtn.disabled = true;
        btnText.textContent = "Stitching Image...";
        loader.style.display = "block";
        errorMsg.textContent = "";

        const resSplit = resolutionSelect.value.split("x");
        const reqWidth = parseInt(resSplit[0]);
        const reqHeight = parseInt(resSplit[1]);
        const isConstrained = document.getElementById('constrain-ratio').checked;
        const padColor = document.getElementById('pad-color').value;

        const payload = {
            west: currentBounds.west,
            south: currentBounds.south,
            east: currentBounds.east,
            north: currentBounds.north,
            width: reqWidth,
            height: reqHeight,
            provider: document.getElementById('provider').value,
            constrain_aspect: isConstrained,
            pad_color: padColor,
            show_scale: document.getElementById('show-scale').checked,
            scale_unit: document.getElementById('scale-unit').value,
            show_graticule: document.getElementById('show-graticule').checked,
            graticule_type: document.getElementById('graticule-type').value
        };

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errJson = await response.json().catch(() => ({}));
                throw new Error(errJson.detail || 'Failed to generate map.');
            }

            // Download Blob
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = downloadUrl;
            
            // Extract filename from header if possible
            const disposition = response.headers.get('Content-Disposition');
            let filename = `map_${payload.width}px.jpg`;
            if (disposition && disposition.indexOf('filename=') !== -1) {
                filename = disposition.split('filename=')[1];
            }
            
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(downloadUrl);
            a.remove();
            
        } catch (err) {
            errorMsg.textContent = err.message;
        } finally {
            // Restore UI State
            generateBtn.disabled = false;
            btnText.textContent = "Generate Map";
            loader.style.display = "none";
        }
    });

    // Run
    initMap();
    loadProviders();
});
