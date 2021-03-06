import sys
import os
import unittest
import math
from osgeo import ogr, gdal
from libdistrict.district import District
from libdistrict.compactness import polsby_popper, schwartzberg, convex_hull_ratio, is_district, has_geometry

class TestHelperMethods(unittest.TestCase):

    def test_not_district(self):

        district = None

        with self.assertRaises(TypeError):
            is_district(district)

    def test_no_geometry(self):

        district = District()

        with self.assertRaises(TypeError):
            has_geometry(district)


class TestPolsbyPopper(unittest.TestCase):

    def test_polsby_popper_not_district(self):

        district = None

        with self.assertRaises(TypeError):
            polsby_popper(district)

    def test_polsby_popper_no_geometry(self):

        district = District()

        with self.assertRaises(TypeError):
            polsby_popper(district)

    def test_polsby_popper_not_geometry(self):

        not_geometry = "Not a geometry"

        district = District(id=id, geometry=not_geometry)

        with self.assertRaises(AttributeError):
            polsby_popper(district)


    def test_polsby_popper_square_4326(self):

        # A square around Lake Merritt: From PlanScore
        geom = ogr.CreateGeometryFromJson('{"type": "Polygon", "coordinates": [[[-122.2631266, 37.7987797], [-122.2631266, 37.8103489], [-122.2484841, 37.8103489], [-122.2484841, 37.7987797], [-122.2631266, 37.7987797]]]}')

        district = District(geometry=geom)

        self.assertAlmostEqual(math.pi/4, polsby_popper(district), places=5)


    def test_polsby_popper_line_4326(self):

        # A thin line through Lake Merritt: From PlanScore
        geom = ogr.CreateGeometryFromJson('{"type": "Polygon", "coordinates": [[[-122.2631266, 37.804111], [-122.2631266, 37.804112], [-122.2484841, 37.804112], [-122.2484841, 37.804111], [-122.2631266, 37.804111]]]}')

        district = District(geometry = geom)

        self.assertAlmostEqual(0., polsby_popper(district), places=3)


    def test_polsby_popper_square_3857(self):

        # A square around Lake Winnebago
        geom = ogr.CreateGeometryFromJson('{"type": "Polygon", "coordinates": [[[-9839815.088179024,5505529.83629639],[-9881396.831566159,5468840.062719505],[-9844707.057989275,5427258.31933237],[-9803125.31460214,5463948.092909254],[-9839815.088179024,5505529.83629639]]]}')

        district = District(geometry=geom)

        self.assertAlmostEqual(math.pi/4, polsby_popper(district), places=5)


    def test_polsby_popper_triangle_3857(self):

        # An equilateral triangle around Lake Mendota
        geom = ogr.CreateGeometryFromJson('{"type": "Polygon", "coordinates": [[[-9942183.378309947,5335705.868703798],[-9966678.038775941,5335248.39511508],[-9954034.524793552,5314264.133688814],[-9942183.378309947,5335705.868703798]]]}')

        district = District(geometry=geom)
        triangle_score = (4.0*math.pi) * ((math.sqrt(3.0)/4.0)/9.0)

        self.assertAlmostEqual(triangle_score, polsby_popper(district), places=5)

    def test_polsby_popper_comparison_esri_shapefile(self):

        shape_file = r"tests/tl_2014_55_sldl/tl_2014_55_sldl.shp"

        driver = ogr.GetDriverByName('ESRI Shapefile')

        data_source = driver.Open(shape_file, 0)

        if data_source is None:
            print ("Open failed.\n")
            sys.exit(1)

        layer = data_source.GetLayer()
        layer.ResetReading()

        compact = None
        dispersed = None

        for feature in layer:

            # feature field one is the district ID
            id = feature.GetField(1)

            # compact
            if id == "027":
                # the feature's geometry
                geom = feature.GetGeometryRef()
                geometry = geom.Clone()
                compact = District(id=27, geometry=geometry)

            # dispersed
            if id == "077":
                # the feature's geometry
                geom = feature.GetGeometryRef()
                geometry = geom.Clone()
                dispersed = District(id=77, geometry=geometry)

        compact_score = polsby_popper(compact)
        dispersed_score = polsby_popper(dispersed)

        self.assertTrue(compact_score > dispersed_score)


class TestSchwartzberg(unittest.TestCase):

    def test_schwartzberg_square_4326(self):

        # A square around Lake Merritt: From PlanScore
        geom = ogr.CreateGeometryFromJson('{"type": "Polygon", "coordinates": [[[-122.2631266, 37.7987797], [-122.2631266, 37.8103489], [-122.2484841, 37.8103489], [-122.2484841, 37.7987797], [-122.2631266, 37.7987797]]]}')

        district = District(geometry=geom)

        radius = math.sqrt(1/math.pi)

        circumference = 2*math.pi*radius

        schwartzberg_score = 1/(4/circumference)

        self.assertAlmostEqual(schwartzberg_score, schwartzberg(district), places=5)


    def test_schwartzberg_square_3857(self):

        # A square around Lake Winnebago
        geom = ogr.CreateGeometryFromJson('{"type": "Polygon", "coordinates": [[[-9839815.088179024,5505529.83629639],[-9881396.831566159,5468840.062719505],[-9844707.057989275,5427258.31933237],[-9803125.31460214,5463948.092909254],[-9839815.088179024,5505529.83629639]]]}')

        district = District(geometry=geom)

        radius = math.sqrt(1/math.pi)

        circumference = 2*math.pi*radius

        schwartzberg_score = 1/(4/circumference)

        self.assertAlmostEqual(schwartzberg_score, schwartzberg(district), places=5)

    def test_schwartzberg_triangle_3857(self):

        # An equilateral triangle around Lake Mendota
        geom = ogr.CreateGeometryFromJson('{"type": "Polygon", "coordinates": [[[-9942183.378309947,5335705.868703798],[-9966678.038775941,5335248.39511508],[-9954034.524793552,5314264.133688814],[-9942183.378309947,5335705.868703798]]]}')

        district = District(geometry=geom)

        area_of_triangle = math.sqrt(3)/4

        radius = math.sqrt(area_of_triangle/math.pi)

        circumference = 2*math.pi*radius

        schwartzberg_score = 1/(3/circumference)

        self.assertAlmostEqual(schwartzberg_score, schwartzberg(district), places=5)


    def test_schwartzberg_comparison_esri_shapefile(self):

        shape_file = r"tests/tl_2014_55_sldl/tl_2014_55_sldl.shp"

        driver = ogr.GetDriverByName('ESRI Shapefile')

        data_source = driver.Open(shape_file, 0)

        if data_source is None:
            print ("Open failed.\n")
            sys.exit(1)

        layer = data_source.GetLayer()
        layer.ResetReading()

        compact = None
        dispersed = None

        for feature in layer:

            # feature field one is the district ID
            id = feature.GetField(1)

            # compact
            if id == "027":
                # the feature's geometry
                geom = feature.GetGeometryRef()
                geometry = geom.Clone()
                compact = District(id=27, geometry=geometry)

            # dispersed
            if id == "077":
                # the feature's geometry
                geom = feature.GetGeometryRef()
                geometry = geom.Clone()
                dispersed = District(id=77, geometry=geometry)

        compact_score = schwartzberg(compact)
        dispersed_score = schwartzberg(dispersed)

        self.assertTrue(compact_score > dispersed_score)


class TestConvexHullRatio(unittest.TestCase):

    # The ratio of the area of the district to the area of the minimum
    # convex polygon that can enclose the ditrict's geometry

    # Area / (Area of minimum convex polygon)

    def test_convex_hull_square_4326(self):

        # A square around Lake Merritt: From PlanScore
        geom = ogr.CreateGeometryFromJson('{"type": "Polygon", "coordinates": [[[-122.2631266, 37.7987797], [-122.2631266, 37.8103489], [-122.2484841, 37.8103489], [-122.2484841, 37.7987797], [-122.2631266, 37.7987797]]]}')

        district = District(geometry=geom)

        self.assertAlmostEqual(1.0, convex_hull_ratio(district), places=5)

    def test_convex_hull_line_4326(self):

        # A thin line through Lake Merritt: From PlanScore
        geom = ogr.CreateGeometryFromJson('{"type": "Polygon", "coordinates": [[[-122.2631266, 37.804111], [-122.2631266, 37.804112], [-122.2484841, 37.804112], [-122.2484841, 37.804111], [-122.2631266, 37.804111]]]}')

        district = District(geometry = geom)

        self.assertAlmostEqual(1.0, convex_hull_ratio(district), places=3)

    def test_convex_hull_square_3857(self):

        # A square around Lake Winnebago
        geom = ogr.CreateGeometryFromJson('{"type": "Polygon", "coordinates": [[[-9839815.088179024,5505529.83629639],[-9881396.831566159,5468840.062719505],[-9844707.057989275,5427258.31933237],[-9803125.31460214,5463948.092909254],[-9839815.088179024,5505529.83629639]]]}')

        district = District(geometry=geom)

        self.assertAlmostEqual(1.0, convex_hull_ratio(district), places=5)

    def test_convex_hull_triangle_3857(self):
        # An equilateral triangle around Lake Mendota
        geom = ogr.CreateGeometryFromJson('{"type": "Polygon", "coordinates": [[[-9942183.378309947,5335705.868703798],[-9966678.038775941,5335248.39511508],[-9954034.524793552,5314264.133688814],[-9942183.378309947,5335705.868703798]]]}')

        district = District(geometry=geom)

        self.assertAlmostEqual(1.0, convex_hull_ratio(district), places=5)

    def test_convex_hull_star_3857(self):
        # A star in the continental 48

        star = ogr.CreateGeometryFromJson('{"type": "Polygon", "coordinates": [[[-12146761.038853927,5875255.742111786],[-11809365.518752303,5017520.836898427],[-12525054.307214756,4436715.824286485],[-11613536.329536539,4300041.463210875],[-11468388.828200482,3389834.284892711],[-10894266.370623887,4110894.8290304607],[-10033430.080825375,3781492.6633242397],[-10370825.600927,4639227.568537598],[-9655136.812464546,5220032.581149541],[-10566654.790142763,5356706.942225151],[-10711802.291478822,6266914.120543315],[-11285924.749055414,5545853.576405566],[-12146761.038853927,5875255.742111786]]]}')
        area = star.GetArea()

        hexagon = ogr.CreateGeometryFromJson('{"type": "Polygon", "coordinates": [[[-12146761.038853927,5875255.742111786],[-12525054.307214756,4436715.824286485],[-11468388.828200482,3389834.284892711],[-10033430.080825375,3781492.6633242397],[-9655136.812464546,5220032.581149541],[-10711802.291478822,6266914.120543315],[-12146761.038853927,5875255.742111786]]]}')
        convex_hull = hexagon.GetArea()

        district = District(geometry=star)

        self.assertAlmostEqual((area/convex_hull), convex_hull_ratio(district), places=5)

    def test_convex_hull_comparison_esri_shapefile(self):

        shape_file = r"tests/tl_2014_55_sldl/tl_2014_55_sldl.shp"

        driver = ogr.GetDriverByName('ESRI Shapefile')

        data_source = driver.Open(shape_file, 0)

        if data_source is None:
            print ("Open failed.\n")
            sys.exit(1)

        layer = data_source.GetLayer()
        layer.ResetReading()

        compact = None
        dispersed = None

        for feature in layer:

            # feature field one is the district ID
            id = feature.GetField(1)

            # compact
            if id == "027":
                # the feature's geometry
                geom = feature.GetGeometryRef()
                geometry = geom.Clone()
                compact = District(id=27, geometry=geometry)

            # dispersed
            if id == "019":
                # the feature's geometry
                geom = feature.GetGeometryRef()
                geometry = geom.Clone()
                dispersed = District(id=19, geometry=geometry)

        compact_score = convex_hull_ratio(compact)
        dispersed_score = convex_hull_ratio(dispersed)

        self.assertTrue(compact_score > dispersed_score)
