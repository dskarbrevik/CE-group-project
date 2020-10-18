# Twitter Scraper

This contains the files needed to create a Docker container that will run a script that streams tweets from a given topic.

One file `config.json` is missing from this repo that contains the Twitter API credentials as well as the Twitter terms to stream from. I think ultimately the values here will be environment variables in the CodeBuild project or secrets stored in Secrets Manager.

I'm currently rate limiting the stream to avoid ultimately running up the AWS bill.

Also, currently the tweets just fall into a bottomless pit (not configured to push anywhere), but can easily be hooked up to go to a Kinesis Data Stream, a Lambda function, a DynamoDB table, an S3 bucket, etc...
