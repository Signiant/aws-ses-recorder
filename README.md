# aws-ses-recorder
These lambda functions processes SES email deliveries and bounces and writes them to dynamoDB tables.  To install and use these:

1) Create a CloudFormation stack using the template here.  This will create the required dynamoDB tables and SNS topics

3) Create the lambda functions using the source code here.  There are 2 functions - one handles bounces, one handles deliveries
- For both functions, the attributes are as follows:
* Handler: lambda_function.lambda_handler
* Role: the role you have created in step 2
* Memory: 128MB
* Timeout: 10s
