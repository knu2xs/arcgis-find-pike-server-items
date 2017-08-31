import unittest
from utilities import *

class UtilityTestCase(unittest.TestCase):

    def test_login(self):
        web_gis = df_web_gis.loc['retail']
        gis = arcgis.gis.GIS(
            url=web_gis.url,
            username=web_gis.username,
            password=web_gis.password
        )
        self.assertEqual('https://commteamretail.maps.arcgis.com', gis._con._parsed_org_url)

    def test_server_in_url_amazon_true(self):
        test_url = 'http://ec2-54-210-26-63.compute-1.amazonaws.com:6080/arcgis/rest/services/DamageAssessment/GlobalStores_Assessment/FeatureServer/0'
        self.assertTrue(server_in_url(test_url))

    def test_server_in_url_amazon_false(self):
        test_url = 'http://ec2-55-210-26-63.compute-1.amazonaws.com:6080/arcgis/rest/services/DamageAssessment/GlobalStores_Assessment/FeatureServer/0'
        self.assertFalse(server_in_url(test_url))

    def test_server_in_url_pike_true(self):
        test_url = 'http://services.pike.com/PMTtzuTB6WiPuNSv/arcgis/rest/services/National_Stores/FeatureServer/0'
        self.assertTrue(server_in_url(test_url))

    def test_server_in_url_pike_false(self):
        test_url = 'http://services.arcgis.com/PMTtzuTB6WiPuNSv/arcgis/rest/services/National_Stores/FeatureServer/0'
        self.assertFalse(server_in_url(test_url))


class RetailTestCase(unittest.TestCase):

    def setUp(self):

        self.web_gis = df_web_gis.loc['retail']

        self.gis = arcgis.gis.GIS(
            url=self.web_gis.url,
            username=self.web_gis.username,
            password=self.web_gis.password
        )

    def test_get_offendeing_maps_data_frame_for_organization(self):

        result = get_offendeing_maps_data_frame_for_organization(self.web_gis, self.gis)

        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
