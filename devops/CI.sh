################################
#Miscellaneous AWSCLI commands to setup CI/CD pipeline
################################

#Initial project creation setup
aws cloudformation create-stack --stack-name ratingsapi-pipeline \
 --template-body file://templates/code_pipeline.yml \
 --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND


git init

#replace <Host> with your Host alias found in ~/.ssh/config
git remote add origin ssh://<Host>/v1/repos/ratingsapi

git fetch origin

#initial project commits to trigger pipeline
git add -f tests/requirements_dev.txt tests/requirements_prod.txt

git commit -m "Initial Project commit"

git push origin master

git checkout -b dev

git add * 

git commit -m "Initial code pipeline commit"

git push origin -u dev


#Create a changeset
aws cloudformation create-change-set --stack-name ratingsapi-pipeline \
 --template-body file://templates/.yml \
 --change-set-name CodePipelineAddition \
 --capabilities CAPABILITY_NAMED_IAM

#Need arn to execute change set
aws cloudformation execute-change-set --change-set-name \
<changeset_arn>

aws cloudformation update-stack --stack-name ratingsapi-pipeline \
 --template-body file://templates/code_pipeline.yml \
 --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND


##allows for much more detailed error logging for stack
#creation events
aws cloudformation describe-stack-events \
--stack-name ratingsapi-pipeline > pipeline_cf_events.json


