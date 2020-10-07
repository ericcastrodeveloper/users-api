from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from json import dumps
from botocore.exceptions import ClientError
from pprint import pprint
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('Users')
application = Flask(__name__)
api = Api(application)


class Users(Resource):

    @application.route('/')
    def hello():
        return '<h1>Ola FIAP!</h1>\nMBA! o/'

    def get(self):
        response = table.scan()
        data = response['Items']
        while 'LastEvaluatedKey' in response:
            response = \
                table.scan(ExclusiveStartKey=response['LastEvaluatedKey'
                           ])
            data.extend(response['Items'])
        return jsonify(data)

    def post(self):
        id = request.json['id']
        name = request.json['name']
        email = request.json['email']
        password = request.json['password']

        response = table.put_item(Item={
            'id': id,
            'name': name,
            'email': email,
            'password': password,
            })

        return jsonify(response)

    def put(self):
        id = request.json['id']
        name = request.json['name']
        email = request.json['email']
        password = request.json['password']

        response = table.update_item(
            Key={'id': id},
            UpdateExpression='set #name=:n, password=:p, email=:e',
            ExpressionAttributeValues={
                ':n': name, ':p': password,
                ':e': email
                }, 
            ExpressionAttributeNames={
            "#name": "name"
                },
                ReturnValues='UPDATED_NEW')
        return jsonify(response)


class UserById(Resource):

    def delete(self, id):
        try:
            response = table.delete_item(Key={'id': id})
        except ClientError as e:

            if e.response['Error']['Code'] \
                == 'ConditionalCheckFailedException':
                print (e.response['Error']['Message'])
            else:
                raise
        else:
            return response
        return {'status': 'success'}

    def get(self, id):
        try:
            response = table.get_item(Key={'id': id})
        except ClientError as e:
            print (e.response['Error']['Message'])
        else:
            return jsonify(response['Item'])


api.add_resource(Users, '/users')
api.add_resource(UserById, '/users/<id>')

if __name__ == '__main__':
    application.run(host='0.0.0.0',debug=True)
