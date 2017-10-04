from urllib2 import Request, urlopen

headers = {
	'Content-Type: application/json',
	'token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjF9._w3BTSmEExK-HHhkmIXq6t9PuSGzaQlBEcimP4mHqoA'
	}
request = Request('http://edi.iem.pw.edu.pl/bach/mail/api/messages/unread/count', headers = headers)

#response_body = urlopen(request).read()
response = urlopen(request)
print response
print response
