# cloud-excellence-group-project

Cloud Excellence group project to take in tweets from Twitter streaming service and output some interesting metrics to a web app.

Check the "Team 1 Project Brief" powerpoint file for more details and a demo of the project.

## Application Workflow

1) ECS container has Python script that is streaming data using Twitter's streaming API.
2) Streamed tweets get processed through lambda function.
3) Lambda functions places results in Dynamodb table.
4) ElasticBeanstalk application pulls data from Dynamodb table to display in dashboard.


