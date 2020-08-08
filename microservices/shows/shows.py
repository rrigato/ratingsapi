import boto3
import json
import logging
import os

from boto3.dynamodb.conditions import Key


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


def clean_show_path_parameter(show_name):
    """Validates the show path parameter

        Parameters
        ----------
        show_name : str
            Name of the show to request

        Returns
        -------
        valid_show_name : boolean
            

        Raises
        ------
    """
    if len(show_name) > 500:
        return (False)

    return(show_name.isascii())


def lambda_proxy_response(status_code, headers_dict, 
    response_body):
    """lambda proxy response handler

        Parameters
        ----------
        status_code : int
            status code of the response

        headers_dict : dict 
            dict for headers

        response_body : dict
            response body to return as string
        

        Returns
        -------
        lambda_proxy_response : dict
            lambda proxy response formatted as apigateway 
            version 2.0 payload
            

        Raises
        ------
    """
    return(
            {
                "statusCode": status_code,
                "isBase64Encoded": False,
                "headers": headers_dict,
                "body": json.dumps(response_body)
            }
    )

def dynamodb_show_request(show_name):
    """Query using the SHOW_ACCESS GSI

        Parameters
        ----------
        show_name : str
            Name of the show to request

        Returns
        -------

        Raises
        ------
    """
    if os.environ.get("DYNAMO_TABLE_NAME") is None:
        dynamo_table_name = "prod_toonami_ratings"
    else:
        dynamo_table_name = os.environ.get("DYNAMO_TABLE_NAME")

    dynamo_client, dynamo_table = get_boto_clients(
            resource_name="dynamodb",
            region_name="us-east-1",
            table_name=dynamo_table_name
    )
    
    '''
        Query one show using the GSI
    '''
    show_access_query = dynamo_table.query(
        IndexName="SHOW_ACCESS",
        KeyConditionExpression=Key("SHOW").eq(show_name)
    )



def main():
    """Entry point into the script
        Parameters
        ----------

        Returns
        -------

        Raises
        ------
    """
    return(
            {
                "statusCode": 200,
                "isBase64Encoded": False,
                "headers": { 
                    "headerName": "headerValue",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({})
            }
        
    )

def lambda_handler(event, context):
    """Handles lambda invocation from cloudwatch events rule

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
    """
    '''
        Logging required for cloudwatch logs
    '''
    logging.getLogger().setLevel(logging.INFO)

    logging.info("main - Lambda proxy event: ")
    logging.info(event)
    return(main())


if __name__ == "__main__":   
    main()
