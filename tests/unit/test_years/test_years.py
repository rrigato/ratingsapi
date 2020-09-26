
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

    @patch("microservices.years.years.get_boto_clients")
    def test_dynamodb_year_request(self, get_boto_clients_mock):
        """tests dynamodb_year_request is called with the correct arguements

        """
        from microservices.years.years import dynamodb_year_request
        from boto3.dynamodb.conditions import Key

        mock_dynamodb_resource = MagicMock()

        valid_year_response = {
            "Items": [{"TOTAL_VIEWERS": "727", "PERCENTAGE_OF_HOUSEHOLDS": "0.50", "YEAR": Decimal("2013"), "SHOW": "Star Wars the Clone Wars", "TIME": "3:00", "RATINGS_OCCURRED_ON": "2013-08-17"}, {"TOTAL_VIEWERS": "683", "PERCENTAGE_OF_HOUSEHOLDS": "0.60", "YEAR": Decimal("2013"), "SHOW": "Star Wars the Clone Wars", "TIME": "3:00", "RATINGS_OCCURRED_ON": "2013-08-24"}, {"TOTAL_VIEWERS": "638", "YEAR": Decimal("2013"), "SHOW": "Star Wars the Clone Wars", "TIME": "2:45", "RATINGS_OCCURRED_ON": "2013-08-31"}],
            "Count": 0, 
            "ScannedCount": 0, 
            "ResponseMetadata": {}
        }
        mock_dynamodb_resource.query.return_value = valid_year_response

        '''
            return None for client, mock for dynamodb table resource
        '''
        get_boto_clients_mock.return_value = (None, mock_dynamodb_resource)
        
        mock_year = 2020


        error_message, dyanmodb_years = dynamodb_year_request(year=mock_year)

        mock_dynamodb_resource.query.assert_called_once_with(
            IndexName="YEAR_ACCESS",
            KeyConditionExpression=Key("YEAR").eq(mock_year)
        )

    @patch("microservices.years.years.get_boto_clients")
    def test_dynamodb_year_request_404(self, get_boto_clients_mock):
        """tests dynamodb_year_request for no year match http 404

        """
        from microservices.years.years import dynamodb_year_request
        from boto3.dynamodb.conditions import Key

        mock_dynamodb_resource = MagicMock()
        
        '''
            return None for client, mock for dynamodb table resource
        '''
        get_boto_clients_mock.return_value = (None, mock_dynamodb_resource)
        
        mock_year = 2010

        mock_dynamodb_resource.query.return_value = {
            "Items": [], 
            "Count": 0, 
            "ScannedCount": 0, 
            "ResponseMetadata": {}
        }

        error_message, television_ratings = dynamodb_year_request(year=mock_year)

        self.assertEqual(error_message, {
            "message": "year: {year} not found".format(
                year=mock_year
                )
            }
        )
        self.assertEqual(television_ratings, [])
        