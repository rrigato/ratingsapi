import boto3
import json
import logging
import os

from boto3.dynamodb.conditions import Key
from datetime import datetime
from microlib.microlib import get_boto_clients
from microlib.microlib import lambda_proxy_response


def clean_path_parameter_string(night):
    """Validates the night path parameter

        Parameters
        ----------
        night : str
            night passed to the request, must be in YYYY-MM-DD
            format

        Returns
        -------
        valid_night : boolean
            
        Raises
        ------
    """
    if type(night) != str:
        logging.info("clean_path_parameter_string - datatype")
        return(False)    
    if len(night) > 10:
        logging.info("clean_path_parameter_string - string length")
        return(False)
    try:
        valid_date_format = datetime.strptime(night, "%Y-%m-%d")        

    except ValueError:
        logging.info("clean_path_parameter_string - Invalid date format")
        return(False)    

    return(True)


def validate_request_parameters(event):
    """Validates the request passed in via the lambda handler event

        Parameters
        ----------
        event : dict
            lambda_handler event from api gateway

        Returns
        -------
        error_response : boolean
            

        Raises
        ------
    """
    error_response = None
    try:
        assert clean_path_parameter_string(event["pathParameters"]["year"]) is True, (
            "year parameter invalid"
        )
        logging.info("validate_request_parameters - year parameter valid")

    except KeyError:
        logging.info("validate_request_parameters - year parameter not found in request")
        error_response = {
            "message": "Path parameter year is required",
            "status_code": 400 
        }

    except AssertionError:
        logging.info("validate_request_parameters - year parameter invalid")
        error_response = {
            "message": "Invalid year path parameter, must be numeric",
            "status_code": 404 
        }

    return(error_response)

def dynamodb_year_request(year):
    """Query using the YEAR_ACCESS GSI

        Parameters
        ----------
        year : int
            year to request

        Returns
        -------
        error_message : dict
            None if items are returned, dict of 404 errors otherwise
        show_ratings : list
            list of dict where each dict is a television show
            rating

        Raises
        ------
    """
    error_message = None

    if os.environ.get("DYNAMO_TABLE_NAME") is None:
        dynamo_table_name = "prod_toonami_ratings"
    else:
        dynamo_table_name = os.environ.get("DYNAMO_TABLE_NAME")

    logging.info("dynamodb_year_request - DYNAMO_TABLE_NAME" + dynamo_table_name)
    dynamo_client, dynamo_table = get_boto_clients(
            resource_name="dynamodb",
            region_name="us-east-1",
            table_name=dynamo_table_name
    )

    logging.info("dynamodb_year_request - year_access_query" )

    '''
        Query one year using the GSI
    '''
    year_access_query = dynamo_table.query(
        IndexName="YEAR_ACCESS",
        KeyConditionExpression=Key("YEAR").eq(int(year))
    )

    show_ratings = year_access_query["Items"]
    logging.info("dynamodb_year_request - Count " + str(year_access_query["Count"]))

    '''
        If no items returned
    '''
    if year_access_query["Count"] == 0:
        error_message = {
            "message": "year: {year_number} not found".format(
                year_number=year
            )
        }
    else:
        logging.info("dynamodb_year_request - preparing year for serialization")
        '''
            convert from decimal to str for json serialization
        '''
        for individual_show in show_ratings:
            try:
                individual_show["YEAR"] = str(individual_show["YEAR"])
            except KeyError:
                logging.info("dynamodb_year_request - No year for " + individual_show["SHOW"])
        
    logging.info(error_message)

    return(error_message, show_ratings)


def main(event):
    """Entry point into the script

        Parameters
        ----------
        event : dict
            api gateway lambda proxy event

        Returns
        -------

        Raises
        ------
    """
    error_response = validate_request_parameters(event=event)

    if error_response is not None:
        status_code = error_response.pop("status_code")
        '''
            return http 400 level error response
        '''
        return(lambda_proxy_response(status_code=status_code, 
        headers_dict={}, response_body=error_response))


    error_message, year_access_query = dynamodb_year_request(
        year=event["pathParameters"]["year"]
    )

    if error_message is None:
        logging.info("main - returning year_access_query" + str(len(year_access_query)))
        return(
            lambda_proxy_response(status_code=200, headers_dict={}, 
            response_body=year_access_query)
            
        )
    else:
        logging.info("main - error_message " + str(error_message))
        return(
            lambda_proxy_response(status_code=404, headers_dict={}, 
            response_body=error_message)
            
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
    return(main(event=event))


if __name__ == "__main__":   
    main(event={"pathParameters":{"show":"Star Wars the Clone Wars"}})
