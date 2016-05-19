# QuaintEgg #

QuaintEgg is some boiler-plate code for writing quick web applications that perform CRUD operations in some way.
It uses web.py. Currently, it supports sqlite. However, writing a new driver is quite easy (given below).

The advantage of using this code is that:
* One can store/fetch arbitrary serializable objects using a database of one's choice.
* No SQL has to be written anywhere; the code remains clean.
* Includes code to perform authentication of HTTP requests. It uses the boilerplate code. So you have something to start with.
* Has the web.py calls structured nicely, so one doesn't have to reinvent the architecture.

To create a new app with this code,

* Do a checkout using 

`git clone <git_url>`

* Create an app directory

`cd QuaintEgg`
`mkdir -p app/controllers`
`mkdir -p app/tables`

* Define a table: Look at framework/tables/Definition.py as an example
* Create an API call 
	* Add a line in urls.py that points to URL.
	* Create a new controller under app/controllers/ (You can copy Authentication.py, if you don't want to start afresh).
	* If you are just doing a bunch of CRUD operations on a table, the class corresponding to the API call is as simple as:


`class User(ClassicDBController):

	def __init__(self):
		ClassicDBController.__init__(WEBCONFIG, AuthTable);`

	* By default, all calls require prior authentication (using the /framework/auth/login call). 
	* A user created using PUT /framerwork/auth/user can be used for logging in
	* A user can also have different roles. The call validateRole() can be executed before doing anything to check if a user belongs to the right role.

Although some preliminary testing has been done, the code is by and large untested. 
Better versions are to follow.

## LICENSE ##

Copyright 2015 Gokul Chittaranjan, gokulchittaranjan@gmail.com

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.