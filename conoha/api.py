
# -*- coding: utf8 -*-
from urllib.request import Request, urlopen
import json
__ALL__ = 'API Tenant'.split()

class API:
	__baseURI = None
	token = None
	_serviceType = None

	def __init__(self, token=None, baseURIPrefix=None):
		self.token = token
		self.baseURIPrefix = baseURIPrefix

	def _getHeaders(self, h):
		headers={
				'Accept': 'application/json',
				}
		if self.token:
			headers['X-Auth-Token'] = self.token.getAuthToken()
		if h:
			headers.update(h)
		return headers

	def _GET(self, path, data=None, isDeserialize=True, headers=None, method='GET'):
		# set self.__baseURI
		if not self.__baseURI:
			if self.token:
				self.__baseURI = self.token.getEndpointURL(self._serviceType)
			else:
				self.__baseURI = self.getEndpointURL(self._serviceType)

			if self.baseURIPrefix:
				self.__baseURI += self.baseURIPrefix

		if data:
			data = bytes(json.dumps(data), 'utf8')
		req = Request(
				url=self.__baseURI + '/' + path,
				headers=self._getHeaders(headers),
				method=method,
				data=data,
				)
		with urlopen(req) as res:
			resBin = res.read()
			if isDeserialize:
				return json.loads(str(resBin, 'utf8'))
			else:
				return resBin

	def _DELETE(self, *args, **nargs):
		return self._GET(*args, method='DELETE', **nargs)

	def _POST(self, path, data, *args, **nargs):
		return self._GET(path, data, *args, method='POST', **nargs)

	def _PUT(self, path, data, *args, **nargs):
		return self._GET(path, data, *args, method='PUT', **nargs)

class Token(API):
	_serviceType = 'identity'
	conf = None
	token = None
	tenantId = None

	def __init__(self, conf):
		super().__init__()
		self.conf = conf
		path = 'tokens'
		data = { 'auth':{
			'passwordCredentials':{
				'username': conf.get('api', 'user'),
				'password': conf.get('api', 'passwd'),
				},
			}}
		self.tenantId = conf.get('api', 'tenant')
		if self.tenantId:
			data['auth']['passwordCredentials']['tenantId'] = self.tenantId
		res = self._POST(path, data)
		self.token = res['access']['token']

	def getTenantId(self):
		return self.tenantId
	def getAuthToken(self):
		return self.token['id']
	def getEndpointURL(self, name):
		url = self.conf.get('endpoint', name, fallback=None) or self.conf.endpoint[self.conf.get('endpoint', 'region')][name]
		assert(url)
		if '{TENANT_ID}' in url:
			return url.replace('{TENANT_ID}', self.getTenantId())
		return url
