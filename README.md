# sesam-firebase
Reads and writes streams of entities to Firebase Realtime DB.

Sinks and sources defines a path to where in the Firebase DB tree the data should be read or written to.

## sources
The source will create one entity per key, where the key will be the "_id" property of the entities.
```json
{
  "0001": {
    "name": "Foo"
  }
}
```
will become:
```json
[
  {
    "_id": "0001",
    "name": "Foo"
  }
]
```

In order to support since, you need to configure a path you want to use for since values. You will need an index on this path. Add this in the rules section
of your Firebase DB like this (in this case the source path is my-users, and marker path is 'last-modified'):
```json
{
  "rules": {
    "my-users": {
      ".indexOn": ["last-modified"]
    }
  }
}
```

TODO support and document since and recommend Firebase.ServerValue.TIMESTAMP

## sinks
The sink will PUT the entity under a key specified by the "_id" property of the entities it receives. The sink will DELETE entities that has the "_deleted" property
set to true.

If you want to create a server side value inside Firebase when writing entities, you can add a property on your entities like this:
```json
{
  "_id": "foo",
  "last-modified": {
    ".sv": "timestamp"
  }
}
```

(see https://firebase.google.com/docs/reference/rest/database/#section-param-query for more info)

An example of system config: 

```json
{
  "_id": "my-firebase",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "KEYFILE": {
          "type": "service_account",
          "..": ".."
      },
      "PROJECT_ID": "my-firebase-instance",
      "SINCE_PATH": "last-modified"
    },
    "image": "sesam/sesam-firebase-db:latest",
    "port": 5000
  }
}
```

The keyfile is obtained by creating a key for the service account in the Firebase console (request a JSON keyfile).