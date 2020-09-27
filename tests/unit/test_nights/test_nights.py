
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock
from unittest.mock import patch

import json
import os
import requests
import unittest


class NightsUnitTests(unittest.TestCase):
    """Testing nights endpoint logic unit tests only
    """
    @classmethod
    def setUpClass(cls):
        """Unitest function that is run once for the class
        """
        with open("tests/events/nights_proxy_event.json", "r") as lambda_event:
            cls.nights_proxy_event = json.load(lambda_event)

    def test_clean_path_parameter_string(self):
        """validates clean_night_path_parameter logic
        """
        from microservices.nights.nights import clean_path_parameter_string

        self.assertFalse(clean_path_parameter_string(night="a" * 501))
        self.assertFalse(clean_path_parameter_string(night="12345"))
        self.assertTrue(clean_path_parameter_string(night="3005-11-28"))


    def test_validate_request_parameters(self):
        """validates fail early on bad request paramters
        """
        from microservices.nights.nights import validate_request_parameters
        
        self.assertIsNone(validate_request_parameters(event=self.nights_proxy_event))

        mock_error_response = validate_request_parameters(event={})
        self.assertEqual(
            mock_error_response,
            {
                "message": "Path parameter night is required",
                "status_code": 400 
            }

        )

    # @patch("microservices.years.years.get_boto_clients")
    # def test_dynamodb_year_request(self, get_boto_clients_mock):
    #     """tests dynamodb_year_request is called with the correct arguements

    #     """
    #     from microservices.years.years import dynamodb_year_request
    #     from boto3.dynamodb.conditions import Key

    #     mock_dynamodb_resource = MagicMock()

    #     valid_year_response = {
    #         "Items": [{"TOTAL_VIEWERS": "727", "PERCENTAGE_OF_HOUSEHOLDS": "0.50", "YEAR": Decimal("2013"), "SHOW": "Star Wars the Clone Wars", "TIME": "3:00", "RATINGS_OCCURRED_ON": "2013-08-17"}, {"TOTAL_VIEWERS": "683", "PERCENTAGE_OF_HOUSEHOLDS": "0.60", "YEAR": Decimal("2013"), "SHOW": "Star Wars the Clone Wars", "TIME": "3:00", "RATINGS_OCCURRED_ON": "2013-08-24"}, {"TOTAL_VIEWERS": "638", "YEAR": Decimal("2013"), "SHOW": "Star Wars the Clone Wars", "TIME": "2:45", "RATINGS_OCCURRED_ON": "2013-08-31"}],
    #         "Count": 0, 
    #         "ScannedCount": 0, 
    #         "ResponseMetadata": {}
    #     }
    #     mock_dynamodb_resource.query.return_value = valid_year_response

    #     '''
    #         return None for client, mock for dynamodb table resource
    #     '''
    #     get_boto_clients_mock.return_value = (None, mock_dynamodb_resource)
        
    #     mock_year = "2020"


    #     error_message, dyanmodb_years = dynamodb_year_request(year=mock_year)

    #     mock_dynamodb_resource.query.assert_called_once_with(
    #         IndexName="YEAR_ACCESS",
    #         KeyConditionExpression=Key("YEAR").eq(int(mock_year))
    #     )

    # @patch("microservices.years.years.get_boto_clients")
    # def test_dynamodb_year_request_404(self, get_boto_clients_mock):
    #     """tests dynamodb_year_request for no year match http 404

    #     """
    #     from microservices.years.years import dynamodb_year_request
    #     from boto3.dynamodb.conditions import Key

    #     mock_dynamodb_resource = MagicMock()
        
    #     '''
    #         return None for client, mock for dynamodb table resource
    #     '''
    #     get_boto_clients_mock.return_value = (None, mock_dynamodb_resource)
        
    #     mock_year = 2010

    #     mock_dynamodb_resource.query.return_value = {
    #         "Items": [], 
    #         "Count": 0, 
    #         "ScannedCount": 0, 
    #         "ResponseMetadata": {}
    #     }

    #     error_message, television_ratings = dynamodb_year_request(year=mock_year)

    #     self.assertEqual(error_message, {
    #         "message": "year: {year} not found".format(
    #             year=mock_year
    #             )
    #         }
    #     )
    #     self.assertEqual(television_ratings, [])

    # @patch("microservices.years.years.dynamodb_year_request")
    # def test_main_success(self, dynamodb_year_request_mock):
    #     """Tests main function for a successful request
    #     """
    #     from microservices.years.years import main

    #     dynamodb_year_request_mock.return_value = (None, {})

    #     main_success_response = main(
    #         event=self.years_proxy_event
    #     )


    #     dynamodb_year_request_mock.assert_called_once_with(
    #         year=self.years_proxy_event["pathParameters"]["year"]
    #     )


    # @patch("microservices.years.years.dynamodb_year_request")
    # def test_main_error(self, dynamodb_year_request_mock):
    #     """Tests main function with an error response
    #     """
    #     from microservices.years.years import main

    #     dynamodb_year_request_mock.return_value = (None, {})

    #     main_failure_response = main(
    #         event={}
    #     )


    #     self.assertEqual(json.loads(main_failure_response["body"]),
    #         {
    #             "message": "Path parameter year is required"
    #         }
    #     )
    #     self.assertEqual(main_failure_response["statusCode"], 400)




    # @patch("logging.getLogger")
    # @patch("microservices.years.years.main")
    # def test_lambda_handler_event(self, main_mock, 
    #     getLogger_mock):
    #     """Tests passing sample event to lambda_handler
    #     """
    #     from microservices.years.years import lambda_handler

    #     lambda_handler(
    #         event=self.years_proxy_event,
    #         context={}
    #     )

    #     self.assertEqual(
    #         getLogger_mock.call_count,
    #         1
    #     )

    #     '''
    #         Testing call count and args passed
    #     '''
    #     main_mock.assert_called_once_with(
    #         event=self.years_proxy_event
    #     )
