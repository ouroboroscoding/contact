import bottle

bottle.run(
	server='gunicorn', host='127.0.0.1', port=8080,
	reloader=False, interval=1, quiet=False, plugins=None,
	debug=None, timeout=10
)