python-gerrit
=============
Gerrit bindings for python

**The bindings are still a work in progress!**

How to use
----------
* Connect to a server:
```python
    pkey = paramiko.RSAKey(filename="/home/foo/.ssh/id_rsa.pub")
    username = "Bob"
    host = "example.com"
    port = 29418  # Default Gerrit ssh port

    g = Gerrit(host, port, username, pkey)
```

* Query for changes:
```python
    g = Gerrit(host, port, username, pkey)

    # Query for all changes in project 'bar' including comments
    g.query("project:bar", options=[QueryOptions.Comments])
    for change in changes:
    	print change
```

* Add a reviewer:
```python
    g = Gerrit(host, port, username, pkey)

    # Query for all changes in project 'bar' including the current patch-set
    g.query("project:bar", options=[QueryOptions.CurrentPatchSet])
    for change in changes:
    	revision = change['currentPatchSet']['revision']
    	g.set_reviewers(revision, add=[username])
```

* Add a review
```python
    g = Gerrit(host, port, username, pkey)

    # Query for all changes in project 'bar' including the current patch-set
    g.query("project:bar", options=[QueryOptions.CurrentPatchSet])
    for change in changes:
    	revision = change['currentPatchSet']['revision']
    	g.review(revision, message="Hello World!")
```

