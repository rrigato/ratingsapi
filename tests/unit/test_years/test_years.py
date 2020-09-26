
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
        with open("tests/events/years_proxy_event.json", "r") as lambda_event:
            cls.years_proxy_event = json.load(lambda_event)

    def test_clean_path_parameter_string(self):
        """validates clean_year_path_parameter logic
        """
        from microservices.years.years import clean_path_parameter_string

        self.assertFalse(clean_path_parameter_string(year="a" * 501))
        self.assertFalse(clean_path_parameter_string(year="12345"))
        self.assertTrue(clean_path_parameter_string(year="2020"))


    def test_validate_request_parameters(self):
        """lambda handler event validation
        """
        from microservices.years.years import validate_request_parameters
        
        self.assertIsNone(validate_request_parameters(event=self.years_proxy_event))

        mock_error_response = validate_request_parameters(event={})
        self.assertEqual(
            mock_error_response,
            {
                "message": "Path parameter year is required",
                "status_code": 400 
            }

        )
        