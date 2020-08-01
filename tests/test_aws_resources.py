from datetime import datetime
from datetime import timedelta

import boto3
import json
import logging
import os
import requests
import unittest

'''
    Load environment from environment variable
'''
ENVIRON_DEF = os.environ.get("")

if ENVIRON_DEF is None:
    ENVIRON_DEF = "dev"

def get_boto_clients(resource_name, region_name="us-east-1",
    table_name=None):
    '''Returns the boto client for various aws resources

        Parameters
        ----------
        resource_name : str
            Name of the resource for the client

        region_name : str
                aws region you are using, defaults to
                us-east-1

        Returns
        -------
        service_client : boto3.client
            boto3 client for the aws resource in resource_name
            in region region_name

        dynamodb_table_resource : boto3.resource.Table
            boto3 Table resource, only returned if table_name is
            not None
        


        Raises
        ------
    '''

    service_client = boto3.client(
            service_name=resource_name, 
            region_name=region_name
        )

    '''
        return boto3 DynamoDb table resource in addition to boto3 client
        if table_name parameter is not None
    '''
    if table_name is not None:
        dynamodb_table_resource = boto3.resource(
            service_name=resource_name,
            region_name=region_name
        ).Table(table_name)

        return(service_client, dynamodb_table_resource)

    '''
        Otherwise return just a resource client
    '''
    return(service_client)


class AwsDevBuild(unittest.TestCase):
    """Tests AWS resources for dev environment

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
    """
    @classmethod
    def setUpClass(cls):
        '''Unitest function that is run once for the class

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        '''
        cls.PROJECT_NAME="ratingsapi"
        apigw_client = get_boto_clients(resource_name="apigateway")
        all_rest_apis = apigw_client.get_rest_apis()["items"]

        '''
            iterates over all rest apis looking for the rest api id
            with the api name ratingsapi-<environment>
        '''
        for rest_api in all_rest_apis:
            if rest_api["name"] == (cls.PROJECT_NAME + "-" + ENVIRON_DEF):
                cls.restapi_id = rest_api["id"]

        cls.CALLABLE_ENDPOINTS = [
            "v1/shows/{show}"
        ]

    def test_apigateway_resources(self):
        '''Tests the lambda proxy resources

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        '''

        apigw_client = get_boto_clients(resource_name="apigateway")

        apigw_resources = apigw_client.get_resources(
            restApiId=self.restapi_id,
            limit=100
        )["items"]

        apigw_path_list = []
        for apigw_resource in apigw_resources:
            apigw_path_list.append(apigw_resource["path"])

        for api_endpoint in self.CALLABLE_ENDPOINTS:
            self.assertIn(api_endpoint, apigw_path_list)
