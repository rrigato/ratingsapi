import boto3
import json
import logging
import os

from boto3.dynamodb.conditions import Key

from microlib.microlib import get_boto_clients
from microlib.microlib import lambda_proxy_response


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
        lambda_proxy_response(status_code=200, headers_dict={}, 
        response_body={"response": "stub"})
        
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
