
from datetime import datetime
from unittest.mock import MagicMock
from unittest.mock import patch

import json
import os
import requests
import unittest


class MicrolibUnitTests(unittest.TestCase):
    """Testing microlib helper functions

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



    @patch("boto3.client")
    def test_get_boto_clients_no_region(self, boto3_client_mock):
        '''Tests outgoing boto3 client generation when no region is passed

            Parameters
            ----------
            boto3_client_mock : unittest.mock.MagicMock
                Mock object used to patch
                AWS Python SDK

            Returns
            -------


            Raises
            ------
        '''
        from microservices.microlib.microlib import get_boto_clients

        test_service_name="lambda"
        get_boto_clients(resource_name=test_service_name)


        '''
            Default region is us-east-1 for 
            get_boto_clients
        '''
        boto3_client_mock.assert_called_once_with(
            service_name=test_service_name,
            region_name="us-east-1"
        )
    def test_get_boto_clients_table_resource(self):
        """Tests getting a dynamodb table resource from get_boto_clients

            Parameters
            ----------

            Returns
            -------


            Raises
            ------
        """
        from microservices.microlib.microlib import get_boto_clients

        dynamodb_functions_to_test = [
            "put_item",
            "query",
            "scan"
        ]
        '''
            boto3 does not make any calls to 
            aws until you use the resource/client
        '''
        test_service_name = "dynamodb"
        test_table_name = "fake_ddb_table"

        dynamodb_client, dynamodb_table = get_boto_clients(
            resource_name=test_service_name, 
            table_name=test_table_name
        )


        '''
            Testing the objects returned have the needed functions
        '''
        self.assertIn(
            "describe_table",
            dir(dynamodb_client)
        )

        '''
            ensuring we have all needed functions for
            working with a table
        '''
        for dynamodb_function in dynamodb_functions_to_test:
            self.assertIn(
                dynamodb_function,
                dir(dynamodb_table)
            )        
    def test_lambda_proxy_response(self):
        '''validates lambda_proxy_response

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        '''
        from microservices.microlib.microlib import lambda_proxy_response

        mock_success_response = [
                {"showname": "mockshow", "show_rating": 1500},
                {"showname": "mockshow2", "show_rating": 2000}
        ]
        
        lambda_success_response = lambda_proxy_response(
            status_code=200,
            headers_dict={},
            response_body=mock_success_response
        )

        self.assertEqual(lambda_success_response["statusCode"], 200)
        self.assertFalse(lambda_success_response["isBase64Encoded"])
        self.assertEqual(lambda_success_response["body"], json.dumps(mock_success_response))


        mock_show_not_found = {"error": "Show name not found"}
        lambda_error_response = lambda_proxy_response(
            status_code=404,
            headers_dict={"Access-Control-Allow-Origin": "*"},
            response_body=mock_show_not_found
        )

        self.assertEqual(lambda_error_response["statusCode"], 404)
        self.assertFalse(lambda_error_response["isBase64Encoded"])
        self.assertEqual(lambda_error_response["body"], json.dumps(mock_show_not_found))
       

