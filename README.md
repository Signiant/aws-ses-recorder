# aws-ses-recorder
These lambda functions processes SES email deliveries and bounces and writes them to dynamoDB.  To install and use these:

1) Create a CloudFormation stack using the template here.  This will create the required dynamoDB tables
2) Create an IAM role with the policy here.  This allows the lambda function to access dynamoDB
- NOTE: You can restrict this policy further to only the specific tables if you wish
3) Create the lambda functions using the source code here.  There are 2 functions - one handles bounces, one handles deliveries
- For both functions, the attributes are as follows:
* Handler: lambda_function.lambda_handler
* Role: the role you have created in step 2
* Memory: 128MB
* Timeout: 10s

4) Now configure the SNS topic to call the lambda function
	This will vary per account but in general, whichever SNS topic receives deliveries should call the delivery function
	and whichever SNS topic receives bounces should call the bounces function