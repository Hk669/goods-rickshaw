# users/views.py (Add import)
from users.models import OTP
import random
import os
from botocore.exceptions import ClientError
import boto3
from dotenv import load_dotenv
load_dotenv()

def send_otp(phone_number):
    # Generate a 6-digit random OTP
    otp = f"{random.randint(100000, 999999)}"

    # Ensure the phone number is in E.164 format
    formatted_phone = "+91" + phone_number if not phone_number.startswith('+') else phone_number

    # Initialize the SNS client
    try:
        client = boto3.client(
            'sns',
            region_name='ap-south-2',  # Use appropriate region
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
    except Exception as e:
        print(f"Error initializing SNS client: {e}")
        return None, False

    try:
        response = client.publish(
            PhoneNumber=formatted_phone,
            Message=f'Your OTP is {otp}. Valid for 5 minutes.',
            MessageAttributes={
                'AWS.SNS.SMS.SenderID': {
                    'DataType': 'String',
                    'StringValue': 'YourApp'
                },
                'AWS.SNS.SMS.SMSType': {
                    'DataType': 'String',
                    'StringValue': 'Transactional'
                }
            }
        )
        # Check response for success
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print(f"OTP sent successfully. Message ID: {response['MessageId']}")
            # Store OTP in the database
            OTP.objects.create(phone_number=phone_number, otp_code=otp)
            return otp, True
        else:
            print(f"Failed to send OTP. Response: {response}")
            return None, False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"ClientError: {error_code} - {error_message}")
        return None, False
    except Exception as e:
        print(f"Unexpected error sending OTP: {e}")
        return None, False
