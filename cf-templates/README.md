# The CE-CICD-Pipeline 

## The pipeline depends on only one file:

### [cf-templates/cicdPackage.yaml](https://github.com/dskarbrevik/CE-group-project/blob/main/cf-templates/cicdPackage.yaml)

# This may be built in a number of whys, but I've used the following sequence of commands (CLI):

- % cd cf-templates
- % aws cloudformation package --template-file cf-root.yaml --output-template cicdPackage.yaml --s3-bucket team1-cicd-pipeline-staging
- % git add cicdPackage.yaml
- % git commit -m "Updated CICD Stack." cicdPacakge.yaml
- % git push -u origin

## Otherwise, you can deploy this package via the CLI as follows (note, the region is different that our Team's default and the stack name is different):

- % aws cloudformation deploy --region us-east-1 --template-file ./cicdPackage.yaml --stack-name DevStack --capabilities  CAPABILITY_NAMED_IAM


