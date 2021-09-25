__all__ = ['to_kml', 'WrongFormatGeoJson']


class WrongFormatGeoJson(Exception):
    """
    Exception raise when geoJson type is not in [Point, MultiPoint, LineString, MultiLineString,
                                                 Polygon, MultiPolygon, GeometryCollection]
    """


def to_kml(geo_json: dict):
    """
    Convert to kml from geoJson
    """
    return '<?xml version="1.0" encoding="UTF-8"?>' + tag('kml', tag('Document', gen_kml_data(geo_json)))


def gen_kml_data(geo_json: dict):
    """
    Generate kml data based on geojson type.
    """
    geo_type = geo_json.get('type')
    if not geo_type:
        return ''
    if geo_type == 'FeatureCollection':
        features = geo_json.get('features')
        if not features:
            return ''
        return ''.join([geo_feature(feature) for feature in features])
    elif geo_type == 'Feature':
        return geo_feature(geo_json)
    else:
        return geo_feature({'type': 'Feature', 'geometry': geo_json})


def geo_feature(geo_data: dict):
    """
    Generate Placemark tag kml
    """
    geometry = geo_data.get('geometry')
    if geometry is None:
        return ''
    if not is_geometry_valid(geometry):
        return ''
    kml_str = geometry_converter(geometry)
    if not kml_str:
        return ''
    return tag('Placemark', kml_str)


def geo_point(geo_data: dict):
    """
    Generate Point tag kml
    """
    coords = geo_data.get('coordinates', [])
    return tag('Point', tag('coordinates', ','.join(coords)))


def geo_multi_point(geo_data: dict):
    """
    Generate MultiGeometry tag kml
    """
    coords = geo_data.get('coordinates', [])
    if not len(coords):
        return ''
    return tag('MultiGeometry', ''.join([geo_point({'coordinates': coord}) for coord in coords]))


def geo_line_string(geo_data: dict):
    """
    Generate LineString tag kml
    """
    coords = geo_data.get('coordinates', [])
    return tag('LineString', tag('coordinates', gen_linear_ring(coords)))


def geo_multi_line_string(geo_data: dict):
    """
    Generate MultiGeometry tag kml
    """
    coords = geo_data.get('coordinates', [])
    if not len(coords):
        return ''
    return tag('MultiGeometry', ''.join([geo_line_string({'coordinates': coord}) for coord in coords]))


def geo_polygon(geo_data: dict):
    """
    Generate Polygon tag kml
    """
    coords = geo_data.get('coordinates', [])
    if not len(coords):
        return ''
    outer = coords[0]
    inners = coords[1:]
    outer_ring = tag('outerBoundaryIs', tag('LinearRing', tag('coordinates', gen_linear_ring(
        outer))))
    inner_rings = ''.join(
        [tag('innerBoundaryIs',
             tag('LinearRing',
                 tag('coordinates', gen_linear_ring(inner)))) for inner in inners])

    return tag('Polygon', outer_ring + inner_rings)


def geo_multi_polygon(geo_data: dict):
    """
    Generate MultiGeometry tag kml
    """
    coords = geo_data.get('coordinates', [])
    if not len(coords):
        return ''
    return tag('MultiGeometry', ''.join([geo_polygon({'coordinates': coord}) for coord in coords]))


def geo_geometry_collection(geo_data: dict):
    """
    Generate MultiGeometry tag kml from geometries geojson
    """
    geometries = geo_data.get('geometries', [])
    if not len(geometries):
        return ''
    return tag('MultiGeometry', ''.join([geometry_converter(geometry) for geometry in geometries]))


def geometry_converter(geometry: dict):
    """
    Choose generation function to convert these field in geojson to kml
    """
    geo_type = geometry.get('type', '')
    geo_mapping = {
        'Point': geo_point,
        'MultiPoint': geo_multi_point,
        'LineString': geo_line_string,
        'MultiLineString': geo_multi_line_string,
        'Polygon': geo_polygon,
        'MultiPolygon': geo_multi_polygon,
        'GeometryCollection': geo_geometry_collection
    }
    try:
        geo_fn = geo_mapping[geo_type]
    except KeyError:
        raise WrongFormatGeoJson(f'{geo_type} is not a valid type in geojson file')
    else:
        return geo_fn(geometry)


def is_geometry_valid(geo_data: dict):
    """
    Check geojson valid
    """
    return ((geo_data.get('type') is not None
             and geo_data.get('coordinates') is not None)
            or (geo_data.get('GeometryCollection') is not None
                and geo_data.get('geometries') is not None
                and all([is_geometry_valid(geometry) for geometry in geo_data.get('geometries')])))


def gen_linear_ring(coords: list):
    """
    Generate linear ring
    """
    return '\n'.join([','.join(map(str, coord)) for coord in coords])


def tag(tag_name: str, data: str):
    """
    Generate tag include tag name and tag data
    """
    return '<' + tag_name + '>' + data + '</' + tag_name + '>'
