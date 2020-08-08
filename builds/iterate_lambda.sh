#!/bin/bash
cd microservices

# iterate over all directories in microservices
for lambda_code in */ ; do 
  if [[ -d "$lambda_code" && ! -L "$lambda_code" ]]; then
    #shows/ to shows
    endpoint_name="${lambda_code%/}"
    echo "$endpoint_name is a directory"; 

    #add microlib module
    cp -r ../../microlib .

    cd $endpoint_name
    #create deployment archive
    zip -r9 "${endpoint_name}.zip" .

    #updates zip deployment package
    aws lambda update-function-code \
            --function-name "${PROJECT_NAME}-${endpoint_name}-endpoint-${BUILD_ENVIRONMENT}" \
            --zip-file "fileb://${endpoint_name}.zip"

    #changes lambda handler to shows.lambda_handler
    aws lambda update-function-configuration \
            --function-name "${PROJECT_NAME}-${endpoint_name}-endpoint-${BUILD_ENVIRONMENT}" \
            --handler "${endpoint_name}.lambda_handler" \
            --runtime python3.8

    mv "${endpoint_name}.zip" ..
          
    cd ..

          #lambda function name
    echo "${PROJECT_NAME}-${endpoint_name}-endpoint-${BUILD_ENVIRONMENT}"
  fi; 
done

cd ..