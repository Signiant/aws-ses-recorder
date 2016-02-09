# aws-ses-recorder
These lambda functions processes SES email deliveries and bounces and writes them to dynamoDB tables.  To install and use these:

1) Create a CloudFormation stack using the template here.  This will create the required dynamoDB tables and SNS topics

2) Create the lambda functions using the [lambda-promotion](https://github.com/Signiant/lambda-promotion) tool.  
There are 2 functions - one handles bounces, one handles deliveries  

To deploy these functions :
  * run npm install in the app directory to install the build dependencies
  * run grunt to execute the build
  * execute the lambda-promotion tool, providing the absolute path to the dist directory (created by grunt), and prod as argument  

If you wish to deploy without the tool:
  *	Create an iam role with the policy found in the deploy directory
  * Create new functions using the source code here, the role you created, and the configuration values specified in the deploy/environments/prod.lam.json file.
  * Configure each lambda function's event source mappings so that they are invoked by the corresponding SNS topic.
