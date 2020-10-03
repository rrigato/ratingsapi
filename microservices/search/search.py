import boto3
import json
import logging
import os

from boto3.dynamodb.conditions import Key
from datetime import datetime
from microlib.microlib import get_boto_clients
from microlib.microlib import lambda_proxy_response


def clean_query_parameter_string(query_parameter_date):
    """Validates the query date parameters

        Parameters
        ----------
        query_parameter_date : str
            query parameter passed to the request, must be in YYYY-MM-DD
            format

        Returns
        -------
        valid_date : boolean
            True if query_parameter_date is valid in YYYY-MM-DD
            format False otherwise

        valid_date_format : datetime.datetime
            datetime object or None
            
        Raises
        ------
    """
    valid_date_format = None
    if type(query_parameter_date) != str:
        logging.info("clean_query_parameter_string - datatype")
        return(False, valid_date_format)    
    if len(query_parameter_date) > 10:
        logging.info("clean_query_parameter_string - string length")
        return(False, valid_date_format)
    try:
        valid_date_format = datetime.strptime(query_parameter_date, "%Y-%m-%d")        

    except ValueError:
        logging.info("clean_query_parameter_string - Invalid date format")
        return(False, valid_date_format)    

    return(True, valid_date_format)


def validate_request_parameters(event):
    """Validates the request passed in via the lambda handler event

        Parameters
        ----------
        event : dict
            lambda_handler event from api gateway

        Returns
        -------
        error_response : dict
            None if request is valid. Otherwise a dict with 
            keys status_code and message detailing the error in
            the request

        start_date : datetime.datetime
            converted startDate query parameter or None

        end_date : datetime.datetime
            converted endDate query parameter or None

        Raises
        ------
    """
    error_response = None
    start_date = None
    end_date = None
         
    try:
        
        start_date_valid, start_date = clean_query_parameter_string(
            event["queryStringParameters"]["startDate"]
        )
        logging.info("validate_request_parameters - startDate " + str(start_date))

        end_date_valid, end_date = clean_query_parameter_string(
            event["queryStringParameters"]["endDate"]
        )
        logging.info("validate_request_parameters - endDate " + str(end_date))

        assert start_date_valid is True, (
            "startDate parameter not in YYYY-MM-DD format"
        )

        assert end_date_valid is True, (
            "endDate parameter not in YYYY-MM-DD format"
        )

        logging.info("validate_request_parameters - query parameters valid dates")


        assert start_date <= end_date, (
            "startDate must be less than or equal to endDate"
        )

    except KeyError:
        logging.info("validate_request_parameters - not all query parameters found")
        error_response = {
            "message": "Query parameters startDate and endDate are required",
            "status_code": 400 
        }

    except AssertionError as query_param_error:
        logging.info("validate_request_parameters - night parameter invalid")
        error_response = {
            "message": str(query_param_error),
            "status_code": 404 
        }

    return(error_response, start_date, end_date)


def get_next_url(start_date, end_date):
    """Returns the next_url depending on if the start_date and end_date
        span multiple years

        Parameters
        ----------
        start_date : datetime.datetime
            converted startDate query parameter 

        end_date : datetime.datetime
            converted endDate query parameter

        Returns
        -------
        next_url : str
            path and query parameters for the next paginated api call

        Raises
        ------
    """
    request_path = "/search?startDate={new_start_date}&endDate={same_end_date}"
    
    if end_date.year > datetime.now().year:
        logging.info("get_next_url - end_date is in the future")
        return(None)

    if end_date.year == start_date.year:
        logging.info("get_next_url - start_date == end_date")
        return(None)

    new_start_date = datetime(start_date.year + 1, 1, 1)

    ''' 
        First day of the next year
    '''
    next_url = request_path.format(
        new_start_date= datetime.strftime(new_start_date, "%Y-%m-%d"),
        same_end_date= datetime.strftime(end_date, "%Y-%m-%d"),

    )
    logging.info("get_next_url - request_path " + next_url)
    
    return(next_url)


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


