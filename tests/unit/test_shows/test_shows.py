
from datetime import datetime
from unittest.mock import MagicMock
from unittest.mock import patch

import json
import os
import requests
import unittest


class ShowsUnitTests(unittest.TestCase):
    """Testing shows endpoint logic unit tests only

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
        pass


    @patch("microservices.shows.shows.get_boto_clients")
    def test_main(self, get_boto_clients_mock):
        '''Test for main function

            Parameters
            ----------
            ratings_iteration_mock : unittest.mock.MagicMock
                Mock object to make sure the reddit api is 
                not called

            handle_ratings_iteration_mock : unittest.mock.MagicMock
                Mock object used to ensure no logging is setup
                for the test

            Returns
            -------

            Raises
            ------
        '''
        from microservices.shows.shows import main

        apigw_response = main()


        self.assertEqual(type(apigw_response["body"]), str)

        self.assertEqual(apigw_response["statusCode"], 200 )



    def test_main(self):
        '''validates clean_show_path_parameter logic

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        '''
        from microservices.shows.shows import clean_show_path_parameter

        self.assertFalse(clean_show_path_parameter(show_name="a" * 501))
        self.assertTrue(clean_show_path_parameter(show_name="A show with & and ; and '"))

    @patch("microservices.shows.shows.get_boto_clients")
    def test_dynamodb_show_request(self, get_boto_clients_mock):
        """tests dynamodb_show_request is called with the correct arguements

            Parameters
            ----------
            get_boto_clients_mock : Mocks the get_boto_clients call
            Returns
            -------

            Raises
            ------
        """
        from microservices.shows.shows import dynamodb_show_request
        from boto3.dynamodb.conditions import Key

        mock_dynamodb_resource = MagicMock()
        
        '''
            return None for client, mock for dynamodb table resource
        '''
        get_boto_clients_mock.return_value = (None, mock_dynamodb_resource)
        
        mock_show_name = "mock_show"
        dynamodb_show_request(show_name=mock_show_name)

        mock_dynamodb_resource.query.assert_called_once_with(
            IndexName="SHOW_ACCESS",
            KeyConditionExpression=Key("SHOW").eq(mock_show_name)
        )