import time
import datetime
import picamera
import boto3
import RPi.GPIO as GPIO
import os
import configparser

#setup the config parser:
configParser = configparser.RawConfigParser()
configFilePath = r'config.py'
configParser.read(configFilePath)

#grab the AWS info from config file:
bucket_name = configParser.get('ben_config', 'bucket_name')
key_id = configParser.get('ben_config', 'key_id')
key = configParser.get('ben_config', 'key')

#this instantiates the s3 client objects which we can then call methods against.
s3 = boto3.client('s3', aws_access_key_id=key_id, aws_secret_access_key=key)
now = datetime.datetime.now
pir_pin = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(pir_pin, GPIO.IN)

def intruder():
    print("intruder!")
    for _ in range(2):
        with picamera.PiCamera() as camera:
            picname = str(now())
            print(picname)
            picname = picname.replace(':', '-')
            picname = picname.replace(' ','_')
            print(picname)
            camera.capture(picname + '.jpg')
            print("just snapped a pic.")
            time.sleep(.5)
            #Upload to S3
            fullpicname = (picname + '.jpg')
            content = open(fullpicname, 'rb')
            try:
                s3.put_object(Bucket=bucket_name, Key=fullpicname, Body=content)
                print('pic uploaded to S3')
            except:
                print('ERROR: Could not upload to S3! Skipping this file...')
                os.rename(fullpicname, ('FAILED_TO_UPLOAD_'+fullpicname))


def main_loop():
    try:
        while True:
            time.sleep(.5)
            if GPIO.input(pir_pin):
                intruder()
            else:
                print("all safe and quiet")
    except KeyboardInterrupt:
        print("quitting...")
        GPIO.cleanup()

if __name__ == '__main__':
    main_loop()
    
