import json
import os

from flask import Flask, request, abort
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http

scopes = ['https://www.googleapis.com/auth/firebase.database',
          'https://www.googleapis.com/auth/userinfo.email']
instance = os.environ['PROJECT_ID']
keyfile = json.loads(os.environ['KEYFILE'])

app = Flask(__name__)
http_auth = None


@app.route('/<path>', methods=['GET'])
def get(path):
    since = request.args.get('since')
    since_path = request.args.get('since_path')
    query = ""
    if since_path and since is not None:
        query = "?orderBy=\"%s\"&startAt=%s" % (since_path, since)
        print(query)
    (response, content) = http_auth.request("https://%s.firebaseio.com/%s.json%s" % (instance, path, query),
                                            "GET")
    if response.status != 200:
        abort(response.status, content)

    tree = json.loads(content.decode('utf-8'))
    entities = []
    for id, data in tree.items():
        entity = {"_id": id}
        # TODO drop entities that has since eq since, startAt is fixed to greater than or equal
        if since_path and data.get(since_path) is not None:
            entity["_updated"] = data.get(since_path)
        for key, value in data.items():
            entity[key] = value
        entities.append(entity)
    return json.dumps(entities)


@app.route('/<path>', methods=['POST'])
def post(path):
    # TODO consider using HTTP PATCH to bulk load the changes, DELETEs still have to be one request per entity unless we want to delete the whole path
    entities = request.get_json()
    if isinstance(entities, dict):
        entities = [entities]
    for entity in entities:
        id = entity["_id"]
        if not entity.get("_deleted", False):
            filtered_entity = {k: v for k, v in entity.items() if not k.startswith('_')}
            (response, content) = http_auth.request(
                "https://%s.firebaseio.com/%s/%s.json" % (instance, path, id), "PUT",
                body=json.dumps(filtered_entity))
        else:
            (response, content) = http_auth.request(
                "https://%s.firebaseio.com/%s/%s.json" % (instance, path, id), "DELETE")
        if response.status != 200:
            return abort(response.status, content)
    return "Done!"


if __name__ == '__main__':
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(keyfile, scopes)
    http_auth = credentials.authorize(Http())
    # http-instance cannot be shared between threads
    app.run(threaded=False, debug=True, host='0.0.0.0')
