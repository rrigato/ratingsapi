from copy import deepcopy
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from unittest.mock import MagicMock
from unittest.mock import patch

import json
import os
import unittest


class SearchUnitTests(unittest.TestCase):
    """Testing search endpoint logic unit tests only
    """
    @classmethod
    def setUpClass(cls):
        """Unitest function that is run once for the class
        """
        with open("tests/events/search_proxy_event.json", "r") as lambda_event:
            cls.search_proxy_event = json.load(lambda_event)

    def test_clean_query_parameter_string(self):
        """validates clean_night_path_parameter logic
        """
        from microservices.search.search import clean_query_parameter_string

        query_date_status, query_datetime = clean_query_parameter_string(
            query_parameter_date="a" * 501
        )
        self.assertFalse(query_date_status)
        self.assertIsNone(query_datetime)

        query_date_status, query_datetime = clean_query_parameter_string(
            query_parameter_date="2018/05/26"
        )
        self.assertFalse(query_date_status)
        self.assertIsNone(query_datetime)

        query_date_status, query_datetime = clean_query_parameter_string(
            query_parameter_date="2018-05-26"
        )
        self.assertTrue(query_date_status)
        self.assertEqual(type(query_datetime), type(datetime.now()))


    def test_validate_request_parameters(self):
        """validates fail early on bad request paramters
        """
        from microservices.search.search import validate_request_parameters
        
        mock_error_response, start_date, end_date =  validate_request_parameters(
            event=self.search_proxy_event
        )
        self.assertIsNone(mock_error_response)

        self.assertEqual(
            start_date, 
            datetime.strptime(
                self.search_proxy_event["queryStringParameters"]["startDate"], "%Y-%m-%d"
            )
        )

        self.assertEqual(
            end_date, 
            datetime.strptime(
                self.search_proxy_event["queryStringParameters"]["endDate"], "%Y-%m-%d"
            )
        )

        mock_error_response, start_date, end_date = validate_request_parameters(event={})
        self.assertEqual(
            mock_error_response,
            {
                "message": "Query parameters startDate and endDate are required",
                "status_code": 400 
            }

        )


        invalid_search_request = deepcopy(self.search_proxy_event)

        invalid_search_request["queryStringParameters"]["startDate"] = "2020-04-01"
        invalid_search_request["queryStringParameters"].pop("endDate")
        mock_error_response, start_date, end_date = validate_request_parameters(
            event=invalid_search_request
        )
        self.assertEqual(
            mock_error_response,
            {
                "message": "Query parameters startDate and endDate are required",
                "status_code": 400 
            }

        )  

        invalid_search_request["queryStringParameters"]["endDate"] = "2020-04-01"
        invalid_search_request["queryStringParameters"].pop("startDate")
        mock_error_response, start_date, end_date = validate_request_parameters(
            event=invalid_search_request
        )
        self.assertEqual(
            mock_error_response,
            {
                "message": "Query parameters startDate and endDate are required",
                "status_code": 400 
            }

        )  



        invalid_search_request = deepcopy(self.search_proxy_event)

        invalid_search_request["queryStringParameters"]["startDate"] = "2020-03-01"
        mock_error_response, start_date, end_date = validate_request_parameters(
            event=invalid_search_request
        )
        self.assertEqual(
            mock_error_response,
            {
                "message": "startDate must be less than or equal to endDate",
                "status_code": 404 
            }

        )        

        invalid_search_request["queryStringParameters"]["endDate"] = "2020/04/01"
        mock_error_response, start_date, end_date = validate_request_parameters(
            event=invalid_search_request
        )
        self.assertEqual(
            mock_error_response,
            {
                "message": "endDate parameter not in YYYY-MM-DD format",
                "status_code": 404 
            }

        )    



        invalid_search_request["queryStringParameters"]["startDate"] = "2020/04/01"
        invalid_search_request["queryStringParameters"]["endDate"] = "2020-04-01"
        mock_error_response, start_date, end_date = validate_request_parameters(
            event=invalid_search_request
        )
        self.assertEqual(
            mock_error_response,
            {
                "message": "startDate parameter not in YYYY-MM-DD format",
                "status_code": 404 
            }

        )    

    def test_get_next_url(self):
        """Validates the next_url returned
        """
        from microservices.search.search import get_next_url

        self.assertIsNone(
            get_next_url(
                start_date=datetime(2019, 10, 15),
                end_date=datetime(2019, 11, 10)
            )
        )


        self.assertEqual(
            "/search?startDate=2014-01-01&endDate=2019-11-16",
            get_next_url(
                start_date=datetime(2013, 5, 11),
                end_date=datetime(2019, 11, 16)
            )
        )


        self.assertEqual(
            "/search?startDate=2019-01-01&endDate=2020-11-20",
            get_next_url(
                start_date=datetime(2018, 4, 14),
                end_date=datetime(2020, 11, 20)
            )
        )


        self.assertIsNone(
            get_next_url(
                start_date=datetime.now(),
                end_date=datetime(datetime.now().year + 1, 6, 25 )
            )
        )

    
    def test_filter_ratings_end_date(self):
        """Filter the results when the end date is filtered on
        """
        from microservices.search.search import filter_ratings
        MOCK_RATINGS_DATA = [
            {
                "RATINGS_OCCURRED_ON": "2019-12-22"
            },{
                "RATINGS_OCCURRED_ON": "2019-12-22"
            },{
                "RATINGS_OCCURRED_ON": "2019-12-22"
            },{
                "RATINGS_OCCURRED_ON": "2019-12-29"
            },{
                "RATINGS_OCCURRED_ON": "2019-12-29"
            },{
                "RATINGS_OCCURRED_ON": "2019-12-29"
            },{
                "RATINGS_OCCURRED_ON": "2019-12-15"
            },{
                "RATINGS_OCCURRED_ON": "2019-12-15"
            }
        ]
        search_criteria_ratings = filter_ratings(
            ratings_query_response=deepcopy(MOCK_RATINGS_DATA),
            start_date=datetime(2019, 1, 1),
            end_date=datetime(2019, 12, 22)
        )

        self.assertEqual(len(search_criteria_ratings), 5)

        search_criteria_ratings = filter_ratings(
            ratings_query_response=deepcopy(MOCK_RATINGS_DATA),
            start_date=datetime(2019, 1, 1),
            end_date=datetime(2019, 12, 23)
        )
        self.assertEqual(len(search_criteria_ratings), 5)

        search_criteria_ratings = filter_ratings(
            ratings_query_response=deepcopy(MOCK_RATINGS_DATA),
            start_date=datetime(2019, 1, 1),
            end_date=datetime(2019, 12, 21)
        )
        self.assertEqual(len(search_criteria_ratings), 2)

        search_criteria_ratings = filter_ratings(
            ratings_query_response =deepcopy(MOCK_RATINGS_DATA),
            start_date=datetime(2019, 1, 1),
            end_date=datetime(2019, 12, 30)
        )
        self.assertEqual(len(search_criteria_ratings), 8)


        search_criteria_ratings = filter_ratings(
            ratings_query_response =deepcopy(MOCK_RATINGS_DATA),
            start_date=datetime(2019, 12, 30),
            end_date=datetime(2019, 12, 30)
        )
        self.assertEqual(search_criteria_ratings, [])

        search_criteria_ratings = filter_ratings(
            ratings_query_response =deepcopy(MOCK_RATINGS_DATA),
            start_date=datetime(2019, 12, 15),
            end_date=datetime(2019, 12, 15)
        )
        self.assertEqual(len(search_criteria_ratings), 2)
    
    def test_filter_ratings_start_date(self):
        """Filter the results when the start date is filtered on
        """
        from microservices.search.search import filter_ratings
        MOCK_RATINGS_DATA = [
            {
                "RATINGS_OCCURRED_ON": "2013-02-02"
            },{
                "RATINGS_OCCURRED_ON": "2013-02-02"
            },{
                "RATINGS_OCCURRED_ON": "2013-02-09"
            },{
                "RATINGS_OCCURRED_ON": "2013-02-09"
            },{
                "RATINGS_OCCURRED_ON": "2013-02-02"
            },{
                "RATINGS_OCCURRED_ON": "2013-02-02"
            },{
                "RATINGS_OCCURRED_ON": "2013-08-24"
            },{
                "RATINGS_OCCURRED_ON": "2013-01-05"
            }
        ]
        search_criteria_ratings = filter_ratings(
            ratings_query_response=deepcopy(MOCK_RATINGS_DATA),
            start_date=datetime(2013, 1, 1),
            end_date=datetime(2019, 12, 22)
        )

        self.assertEqual(len(search_criteria_ratings), len(MOCK_RATINGS_DATA))

        search_criteria_ratings = filter_ratings(
            ratings_query_response=deepcopy(MOCK_RATINGS_DATA),
            start_date=datetime(2013, 2, 3),
            end_date=datetime(2019, 12, 23)
        )
        self.assertEqual(len(search_criteria_ratings), 3)

        search_criteria_ratings = filter_ratings(
            ratings_query_response=deepcopy(MOCK_RATINGS_DATA),
            start_date=datetime(2013, 2, 2),
            end_date=datetime(2019, 12, 21)
        )
        self.assertEqual(len(search_criteria_ratings), 7)

        search_criteria_ratings = filter_ratings(
            ratings_query_response =deepcopy(MOCK_RATINGS_DATA),
            start_date=datetime(2013, 8, 21),
            end_date=datetime(2019, 12, 30)
        )
        self.assertEqual(len(search_criteria_ratings), 1)



    @patch("microservices.search.search.get_boto_clients")
    def test_dynamodb_year_request(self, get_boto_clients_mock):
        """tests dynamodb_year_request is called with the correct arguements

        """
        from microservices.search.search import dynamodb_year_request
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
        
        mock_year = "2020"


        error_message, dyanmodb_years = dynamodb_year_request(year=mock_year)

        mock_dynamodb_resource.query.assert_called_once_with(
            IndexName="YEAR_ACCESS",
            KeyConditionExpression=Key("YEAR").eq(int(mock_year))
        )

    @patch("microservices.search.search.get_boto_clients")
    def test_dynamodb_year_request_404(self, get_boto_clients_mock):
        """tests dynamodb_year_request for no year match http 404

        """
        from microservices.search.search import dynamodb_year_request
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

    @patch("microservices.search.search.filter_ratings")
    @patch("microservices.search.search.dynamodb_year_request")
    def test_main_success(self, dynamodb_year_request_mock, filter_ratings_mock):
        """Tests main function for a successful request
        """
        from microservices.search.search import main

        dynamodb_year_request_mock.return_value = (None, [])

        filter_ratings_mock.return_value = []

        main_success_response = main(
            event=self.search_proxy_event
        )


        dynamodb_year_request_mock.assert_called_once_with(
            year=int(self.search_proxy_event["queryStringParameters"]["startDate"][0:4])
        )

        filter_ratings_mock.assert_called_once_with(
            ratings_query_response=[],
            start_date=datetime.strptime(
                self.search_proxy_event["queryStringParameters"]["startDate"], "%Y-%m-%d"
            ),
            end_date=datetime.strptime(
                self.search_proxy_event["queryStringParameters"]["endDate"], "%Y-%m-%d"
            ),
        )

        self.assertEqual(
            json.loads(main_success_response["body"]),
            {
                "ratings": [],
                "next": None
            }
        )

    @patch("microservices.search.search.dynamodb_year_request")
    def test_main_error(self, dynamodb_year_request_mock):
        """Tests main function with an error response
        """
        from microservices.search.search import main

        dynamodb_year_request_mock.return_value = (None, {})

        main_failure_response = main(
            event={}
        )


        self.assertEqual(json.loads(main_failure_response["body"]),
            {
                "message": "Query parameters startDate and endDate are required"
            }
        )
        self.assertEqual(main_failure_response["statusCode"], 400)




    @patch("logging.getLogger")
    @patch("microservices.search.search.main")
    def test_lambda_handler_event(self, main_mock, 
        getLogger_mock):
        """Tests passing sample event to lambda_handler
        """
        from microservices.search.search import lambda_handler

        lambda_handler(
            event=self.search_proxy_event,
            context={}
        )

        self.assertEqual(
            getLogger_mock.call_count,
            1
        )

        '''
            Testing call count and args passed
        '''
        main_mock.assert_called_once_with(
            event=self.search_proxy_event
        )
