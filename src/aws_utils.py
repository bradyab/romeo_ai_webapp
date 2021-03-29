import boto3
from boto3.dynamodb.conditions import Key
from . import diff_utils
import time

"""
Given a user, get all the updates for the user's profile
from Amazon DynamoDB.
"""
class ProfileUpdateItem:
  def __init__(self, user_id, timestamp, data_diff):
    self.user_id = user_id
    self.timestamp = timestamp
    self.data_diff = data_diff

aws_access_key_id = "Contact aeb3bs@gmail.com for api keys"
aws_secret_access_key = "Contact aeb3bs@gmail.com for api keys"

def get_profile_updates(user_id: str) -> []:
  client = boto3.client(
    'dynamodb',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name='us-east-2'
  )

  resp = client.query(
    TableName='profile_updates',
    KeyConditionExpression="user_id = :userIdFilter",
    ExpressionAttributeValues={
        ":userIdFilter": {
          "S": user_id
        }
    }
    )

  if 'Items' not in resp:
      return []

  items = resp["Items"]

  parsed_items = []

  for item in items:
    parsed_item = ProfileUpdateItem(
      item['user_id']['S'],
      item['timestamp']['N'],
      item['data_diff']['S']
    )

    parsed_items.append(parsed_item)

  return parsed_items

def create_profile_update(user_id, data_diff) -> str:
  client = boto3.client(
    'dynamodb',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name='us-east-2'
  )

  resp = client.put_item(
    TableName='profile_updates',
    Item={
      "user_id": {
        "S": user_id
      },
      "timestamp": {
        "N": str(time.time())
      },
      "data_diff": {
        "S": data_diff
      }
    }
  )

def recreate_most_recent_data(profile_updates: []) -> str:
  text = ""

  for update in profile_updates:
    text = diff_utils.generate_text(update.data_diff, text)

  return text

def create_profile_update_if_needed(user_id, user_profile):
  profile_updates = get_profile_updates(user_id)

  most_recent_data = recreate_most_recent_data(profile_updates)

  user_profile_str = str(user_profile)

  if most_recent_data == user_profile_str:
    print("No change found in the profile!")
    return;

  data_diff = diff_utils.create_diff(most_recent_data, user_profile_str)

  create_profile_update(user_id, data_diff)

