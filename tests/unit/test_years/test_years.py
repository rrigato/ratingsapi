
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock
from unittest.mock import patch

import json
import os
import requests
import unittest


class YearsUnitTests(unittest.TestCase):
    """Testing years endpoint logic unit tests only

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
    """
    @classmethod
    def setUpClass(cls):
        """Unitest function that is run once for the class

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        """
        with open("tests/events/shows_proxy_event.json", "r") as lambda_event:
            cls.shows_proxy_event = json.load(lambda_event)

    def test_clean_path_parameter_string(self):
        '''validates clean_year_path_parameter logic
        '''
        from microservices.years.years import clean_path_parameter_string

        self.assertFalse(clean_path_parameter_string(year="a" * 501))
        self.assertFalse(clean_path_parameter_string(year="12345"))
        self.assertTrue(clean_path_parameter_string(year="2020"))
