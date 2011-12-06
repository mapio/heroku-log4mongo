heroku-log4mongo
================

.. |flattr| image:: http://api.flattr.com/button/flattr-badge-large.png
  :alt: Flattr this git repo
  :target: http://flattr.com/thing/448158/heroku-log4mongo

|flattr| 

``heroku-log4mongo`` is a demo application showing how to obtain 240MB of free
cloud logging in a `mongodb <http://www.mongodb.org/>`_ for your `Heroku
<http://www.heroku.com/>`_ deployments -- a sort of (very rough) *free
version* of the `Loggly <http://addons.heroku.com/loggly>`_ addon, but with
indefinite *data retention*.

To `use mongodb for logging
<http://blog.mongodb.org/post/172254834/mongodb-is-fantastic-for-logging>`_ is
not a new idea; the (I think original and nice) contribution of this sample
code is to emphasize:

* the very nice `log4mongo-python
  <http://github.com/log4mongo/log4mongo-python>`_ library making all this
  pretty easy,

* the awsome `mongolab <http://mongolab.com/>`_ service, offering *for free* a
  240MB database in the cloud (with a nice web interface);

* a nice hack to make `gunicorn <http://gunicorn.org/>`_ send its *access
  log* to the cloud,

* lasts but not least, how Heroku makes all this quite a piece of cake!

This demo applicaton is based on `Flask <http://flask.pocoo.org/>`_ but every
other framework will work (albeit being less pleasurable to program).

The following part of this README describes how to use the demo application
(locally and on Heroku), for more details on how the code works and the idea
behind it, please check the `blog post
<http://santini.dsi.unimi.it/extras/ph/logging-in-the-cloud-for-free-with-heroku-and-mongolab.html>`_ on my `ProcrastinHacking
<http://santini.dsi.unimi.it/extras/ph/>`_ blog.


Setup Heroku and mongolab
-------------------------

To test this application, setup your Heroku environment as usual (assuming
that the ``heroku`` and ``foreman`` gems are installed)::

  $ git clone git://github.com/mapio/heroku-log4mongo.git
  $ heroku create --stack cedar

then add to it the *free* `mongolab:starter` addon to your app and set the
``VERSION``::

  $ heroku addons:add mongolab:starter
  $ heroku config:add VERSION=production

that will give you a 240MB mongodb hosted in the cloud for free, as easy as
pie! The ``VERSION`` variable is used to distinguish between the local and
deployed versions of the application.


Test locally
------------

You can now setup a loccal testing environment using `virtualenvwrapper
<http://www.doughellmann.com/projects/virtualenvwrapper/>`_::

  $ mktmpenv; cd -
  $ pip install -r requirements.txt

to use the app locally you need to setup the local ``.env`` file used by
``foreman`` to configure your app, in particular you need to store in it the
URI of your databse, and the ``VERSION`` of the application with::

  $ heroku config -s | grep 'MONGOLAB_URI' > .env
  $ echo 'VERSION=developement' >> .env

(or conveniently use the ``./scripts/set_env`` script). You are now ready to
test locally: run the app and access its home with ``curl``::

  $ foreman start -p 8000
  22:13:02 web.1     | started with pid 22744
  22:13:02 web.1     | 2011-12-06 22:13:02 [22745] [INFO] Starting gunicorn 0.13.4
  22:13:02 web.1     | 2011-12-06 22:13:02 [22745] [INFO] Listening at: http://0.0.0.0:8000 (22745)
  22:13:02 web.1     | 2011-12-06 22:13:02 [22745] [INFO] Using worker: sync
  22:13:02 web.1     | 2011-12-06 22:13:02 [22746] [INFO] Booting worker with pid: 22746
  $ curl http://0.0.0.0:8000
  Hello, world!
  22:09:53 web.1     | 2011.12:06 22:09:53 [22691] [DEBUG/APPLICATION] This is an application log message
  22:09:53 web.1     | 2011.12:06 22:09:53 [22691] [INFO/ACCESS] 127.0.0.1 - - [06/Dec/2011:22:09:53] "GET / HTTP/1.1" 200 13 "-" "curl/7.21.4 (universal-apple-darwin11.0) libcurl/7.21.4 OpenSSL/0.9.8r zlib/1.2.5"

the first output lines being the normal app startup, followed by ``curl``
output, then a *log message coming from the application*, and finally a
typical *access log* message.


Deploy
------

You are now ready to try the application in production::

  $ git push heroku master
  $ heroku scale web=1
  $ curl http://<YOUR_APP>.herokuapp.com/

where ``<YOUR_APP>`` is the app name you got as output of the ``heroku
create`` command above. You can now get your logs from the cloud, for instance
using the simple provided script::

  $ ./scripts/get_logs
  4.231.57.32 - - [06/Dec/2011:21:19:08] "GET / HTTP/1.1" 200 13 "-" "curl/7.21.4 (universal-apple-darwin11.0) libcurl/7.21.4 OpenSSL/0.9.8r zlib/1.2.5"
  $ ./scripts/get_logs -e
  2011-12-06 21:15:19+00:00 Starting gunicorn 0.13.4
  2011-12-06 21:15:19+00:00 Listening at: http://0.0.0.0:32652 (3)
  2011-12-06 21:15:19+00:00 Using worker: sync
  2011-12-06 21:15:19+00:00 Booting worker with pid: 10
  $  ./scripts/get_logs -a
  2011-12-06 21:19:08+00:00 This is an application log message

which will respectively output yuor *access log*, *error log* and *application
log*, or you can access the nice web interface provided by the addon with::

  $ heroku addons:open mongolab:starter

When you are down playing with this, don't forget to **scale down**::

  $ heroku scale web=0

not to incur in unanticipated costs!

If you plan to use this in a real production application consider `capped
collections <http://www.mongodb.org/display/DOCS/Capped+Collections>`_ (a very
high performance auto-FIFO database) as a simple way of controlling the size of
your logs.
