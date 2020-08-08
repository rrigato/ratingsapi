import boto3 
import json

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

