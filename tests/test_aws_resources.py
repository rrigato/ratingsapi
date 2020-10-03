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
BUILD_ENVIRONMENT = os.environ.get("BUILD_ENVIRONMENT")

if BUILD_ENVIRONMENT is None:
    BUILD_ENVIRONMENT = "dev"

def get_boto_clients(resource_name, region_name="us-east-1",
    table_name=None):
    """Returns the boto client for various aws resources

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
    """

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
        """Unitest function that is run once for the class

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        """
        cls.PROJECT_NAME="ratingsapi"
        cls.apigw_client = get_boto_clients(resource_name="apigateway")
        all_rest_apis = cls.apigw_client.get_rest_apis()["items"]

        '''
            iterates over all rest apis looking for the rest api id
            with the api name ratingsapi-<environment>
        '''
        for rest_api in all_rest_apis:
            if rest_api["name"] == (cls.PROJECT_NAME + "-" + BUILD_ENVIRONMENT):
                cls.restapi_id = rest_api["id"]


        apigw_resources = cls.apigw_client.get_resources(
            restApiId=cls.restapi_id,
            limit=100
        )["items"]


        '''
            dict where key is the path (ex: /shows/{show})
            and the value is the resource id random string in api gateway 
            that identifies the resource (ex: aaaabc)
        '''
        cls.path_to_resource_id = {}

        for apigw_resource in apigw_resources:
            cls.path_to_resource_id[apigw_resource["path"]] = apigw_resource["id"]


        


    def test_apigateway_stage(self):
        """tests the version stage

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        """

        apigw_client = get_boto_clients(resource_name="apigateway")

        apigw_version_stage = apigw_client.get_stage(
            restApiId=self.restapi_id,
            stageName="v1"
        )
        self.assertTrue(apigw_version_stage["tracingEnabled"])

    def test_nights_endpoint(self):
        """Tests that the night lambda proxy integrations is setup

        """
        apigw_method = self.apigw_client.get_method(
            restApiId=self.restapi_id,
            resourceId=self.path_to_resource_id["/nights/{night}"],
            httpMethod="GET"
        )

        '''
            Test api key is required for lambda proxy and that
            correct lambda arn is used as a backend
        '''
        self.assertTrue(apigw_method["apiKeyRequired"])

        self.assertTrue(apigw_method["methodIntegration"]["uri"].endswith(
            self.PROJECT_NAME + "-nights-endpoint-" + BUILD_ENVIRONMENT + 
            "/invocations"
        ))


    def test_nights_not_found(self):
        """Tests 404 is returned for nights not found
        """
        '''
            invoke a test method for invalid input
        '''
        apigw_error_response = self.apigw_client.test_invoke_method(
            restApiId=self.restapi_id,
            resourceId=self.path_to_resource_id["/nights/{night}"],
            httpMethod="GET",
            pathWithQueryString="/nights/2008-09-27"
        )
        
        self.assertEqual(apigw_error_response["status"], 404)


    @unittest.skipIf(BUILD_ENVIRONMENT != "prod", "Skipping when there is no prod ratings data")
    def test_nights_endpoint_prod(self):
        """tests the nights endpoint where there is production data
        """

        apigw_path_list = []


        '''
            invoke a test method for valid input
        '''
        apigw_response = self.apigw_client.test_invoke_method(
            restApiId=self.restapi_id,
            resourceId=self.path_to_resource_id["/nights/{night}"],
            httpMethod="GET",
            pathWithQueryString="/nights/2014-01-04"
        )


        self.assertEqual(apigw_response["status"], 200)

        first_night_2014 = json.loads(apigw_response["body"])
        '''
            13 television ratings from 2014-01-04
        '''
        self.assertEqual(len(first_night_2014), 13)
        '''
            test structure of random ratings
        '''
        self.assertTrue(first_night_2014[0]["TOTAL_VIEWERS"].isnumeric())

        self.assertTrue(first_night_2014[0]["YEAR"].isnumeric())

    def test_search_endpoint(self):
        """Tests that the search integrations is setup

        """
        apigw_method = self.apigw_client.get_method(
            restApiId=self.restapi_id,
            resourceId=self.path_to_resource_id["/search"],
            httpMethod="GET"
        )

        '''
            Test api key is required for lambda proxy and that
            correct lambda arn is used as a backend
        '''
        self.assertTrue(apigw_method["apiKeyRequired"])

        self.assertTrue(apigw_method["methodIntegration"]["uri"].endswith(
            self.PROJECT_NAME + "-search-endpoint-" + BUILD_ENVIRONMENT + 
            "/invocations"
        ))

    @unittest.skip("Skipping for now")
    def test_search_not_found(self):
        """Tests that 404 is returned if the startDate is greater than the
            endDate
        """
        '''
            invoke a test method for invalid input
        '''
        apigw_error_response = self.apigw_client.test_invoke_method(
            restApiId=self.restapi_id,
            resourceId=self.path_to_resource_id["/years/{year}"],
            httpMethod="GET",
            pathWithQueryString="/search?startDate=2"
        )
        
        self.assertEqual(apigw_error_response["status"], 404)

    @unittest.skip("Skipping for now")
    @unittest.skipIf(BUILD_ENVIRONMENT != "prod", "Skipping when there is no prod ratings data")
    def test_search_endpoint_prod(self):
        """tests the seach endpoint where there is production data
        """

        apigw_path_list = []


        '''
            invoke a test method for valid input
        '''
        apigw_response = self.apigw_client.test_invoke_method(
            restApiId=self.restapi_id,
            resourceId=self.path_to_resource_id["/search"],
            httpMethod="GET",
            pathWithQueryString="/search?startDate=2012-05-26&endDate=2013-05-25"
        )


        self.assertEqual(apigw_response["status"], 200)

        ratings_response = json.loads(apigw_response["body"])
        '''
            should have 
        '''
        self.assertGreater(ratings_response, 500)

        '''
            test structure of random ratings
        '''
        self.assertTrue(ratings_2014[200]["TOTAL_VIEWERS"].isnumeric())

        self.assertTrue(ratings_2014[200]["YEAR"].isnumeric())



    def test_shows_endpoint(self):
        """Tests that the shows lambda proxy integrations is setup

        """
        apigw_method = self.apigw_client.get_method(
            restApiId=self.restapi_id,
            resourceId=self.path_to_resource_id["/shows/{show}"],
            httpMethod="GET"
        )

        '''
            Test api key is required for lambda proxy and that
            correct lambda arn is used as a backend
        '''
        self.assertTrue(apigw_method["apiKeyRequired"])

        self.assertTrue(apigw_method["methodIntegration"]["uri"].endswith(
            self.PROJECT_NAME + "-shows-endpoint-" + BUILD_ENVIRONMENT + 
            "/invocations"
        ))


    def test_shows_not_found(self):
        """Tests 404 is returned for shows not found
        """
        '''
            invoke a test method for invalid input
        '''
        apigw_error_response = self.apigw_client.test_invoke_method(
            restApiId=self.restapi_id,
            resourceId=self.path_to_resource_id["/shows/{show}"],
            httpMethod="GET",
            pathWithQueryString="/shows/Mock a show name"
        )
        
        self.assertEqual(apigw_error_response["status"], 404)



    @unittest.skipIf(BUILD_ENVIRONMENT != "prod", "Skipping when there is no prod ratings data")
    def test_shows_endpoint_prod(self):
        """tests the shows endpoint where there is production data

        """

        apigw_path_list = []


        '''
            invoke a test method for valid input
        '''
        apigw_response = self.apigw_client.test_invoke_method(
            restApiId=self.restapi_id,
            resourceId=self.path_to_resource_id["/shows/{show}"],
            httpMethod="GET",
            pathWithQueryString="/shows/Star Wars the Clone Wars"
        )


        self.assertEqual(apigw_response["status"], 200)

        star_wars_ratings = json.loads(apigw_response["body"])
        '''
            should have at least 50 airing of the show
            Star Wars the Clone Wars
        '''
        self.assertGreater(len(star_wars_ratings), 50)

        '''
            test structure of random ratings
        '''
        self.assertTrue(star_wars_ratings[10]["TOTAL_VIEWERS"].isnumeric())

        self.assertTrue(star_wars_ratings[10]["YEAR"].isnumeric())


    def test_years_endpoint(self):
        """Tests that the year lambda proxy integrations is setup

        """
        apigw_method = self.apigw_client.get_method(
            restApiId=self.restapi_id,
            resourceId=self.path_to_resource_id["/years/{year}"],
            httpMethod="GET"
        )

        '''
            Test api key is required for lambda proxy and that
            correct lambda arn is used as a backend
        '''
        self.assertTrue(apigw_method["apiKeyRequired"])

        self.assertTrue(apigw_method["methodIntegration"]["uri"].endswith(
            self.PROJECT_NAME + "-years-endpoint-" + BUILD_ENVIRONMENT + 
            "/invocations"
        ))


    def test_years_not_found(self):
        """Tests 404 is returned for years not found
        """
        '''
            invoke a test method for invalid input
        '''
        apigw_error_response = self.apigw_client.test_invoke_method(
            restApiId=self.restapi_id,
            resourceId=self.path_to_resource_id["/years/{year}"],
            httpMethod="GET",
            pathWithQueryString="/years/2009"
        )
        
        self.assertEqual(apigw_error_response["status"], 404)

    @unittest.skipIf(BUILD_ENVIRONMENT != "prod", "Skipping when there is no prod ratings data")
    def test_years_endpoint_prod(self):
        """tests the years endpoint where there is production data
        """

        apigw_path_list = []


        '''
            invoke a test method for valid input
        '''
        apigw_response = self.apigw_client.test_invoke_method(
            restApiId=self.restapi_id,
            resourceId=self.path_to_resource_id["/years/{year}"],
            httpMethod="GET",
            pathWithQueryString="/years/2014"
        )


        self.assertEqual(apigw_response["status"], 200)

        ratings_2014 = json.loads(apigw_response["body"])
        '''
            should have 674 television ratings from 2014
        '''
        self.assertGreater(len(ratings_2014), 500)

        '''
            test structure of random ratings
        '''
        self.assertTrue(ratings_2014[100]["TOTAL_VIEWERS"].isnumeric())

        self.assertTrue(ratings_2014[100]["YEAR"].isnumeric())


    @unittest.skip("Skip until custom domain name is setup for API")
    def test_custom_dns(self):
        """tests the custom domain name

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        """
        secretsmanager_client = get_boto_clients(resource_name="secretsmanager")
        '''
            get client id, client secret and domain_url
        '''
        if latest_secrets["ratingsapi_" + BUILD_ENVIRONMENT + "pipeline_client_id"] is None:
            unittest.skip("no client_id in secretsmanager")

        elif latest_secrets["ratingsapi_" + BUILD_ENVIRONMENT + "pipeline_client_secret"] is None:
            unittest.skip("no client_secret environment variable")

        elif latest_secrets["ratingsapi_" + BUILD_ENVIRONMENT + "pipeline_custom_dns"] is None:
            unittest.skip("no client_secret environment variable")

        '''
            test response
        '''
        response_to_test = requests.get(
            latest_secrets["ratingsapi_" + BUILD_ENVIRONMENT + "pipeline_custom_dns"] 
            + "/v1/shows/show"
        )