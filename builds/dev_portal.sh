cd ~/Documents/apidevportal

git init
git remote add aws-dev-portal https://github.com/awslabs/aws-api-gateway-developer-portal.git

git fetch aws-dev-portal

git merge aws-dev-portal/master

CUSTOM_PREFIX="toonamiratings"
S3_ARTIFACT_BUCKET="dev-portal-ratingsapi-prod"

sam package --template-file ./cloudformation/template.yaml \
    --output-template-file ./cloudformation/packaged.yaml \
    --s3-bucket "${S3_ARTIFACT_BUCKET}"


sam deploy --template-file ./cloudformation/packaged.yaml \
    --stack-name "${CUSTOM_PREFIX}-prod-developers-portal" \
    --s3-bucket "${S3_ARTIFACT_BUCKET}" \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides \
    DevPortalSiteS3BucketName="${S3_ARTIFACT_BUCKET}-dev-portal-static-assets" \
    ArtifactsS3BucketName="${S3_ARTIFACT_BUCKET}-dev-portal-artifacts" \
    CognitoDomainNameOrPrefix="${S3_ARTIFACT_BUCKET}"