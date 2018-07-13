# Pachatary API

This repo contains the backend code for Pachatary project.
This simple app aims to be a reference
to discover interesting places
and also to record our past experiences,
sharing content with other people.

Application domain is composed by `scenes`,
which are defined as something that happened
or can be done/seen in a located place.
A group of `scenes` are defined as an `experience`.

A `person` can use api as anonymous guest.
Later, she can register specifying just username and email.
Posterior email confirmation is required to create content.
There is no password, so login will be implemented using email token system.
A registered person has a `profile`.

A `person` can `save` their favourite `experiences`.

For the moment, the api is only consumed by
[pachatary-android](https://github.com/jordifierro/pachatary-android) project.

## API Endpoints

### `GET /experiences?username=self&limit=20`
### `GET /experiences?username=george&limit=20`
### `GET /experiences?saved=true&limit=20`
_Request:_
You can specify `self` username param to fetch only experiences you have created,
or target username to receive that person experiences.
You can also specify `saved=true` filter param to fetch only experiences you have saved.
You can also define a `limit` to let server know
how many elements you do want on each page
(if you skip this param server will return 20).

_Response:_
```json
{
    "results":
        [
            {
                "id": "3",
                "title": "Magic Castle of Lost Swamps",
                "description": "Don't even try to go there!",
                "picture": null,
                "author_profile": {
                    "username": "da_usr",
                    "bio": "about me",
                    "picture": null,
                    "is_me": true,
                },
                "is_mine": false,
                "is_saved": false,
                "saves_count": 5
            },
            {
                "id": "2",
                "title": "Baboon",
                "description": "Mystical place...",
                "picture": {
                    "small_url": "https://experiences/8c29.small.jpg",
                    "medium_url": "https://experiences/8c29.medium.jpg",
                    "large_url": "https://experiences/8c29.large.jpg",
                },
                "author_profile": {
                    "username": "usr.nam",
                    "bio": "user info",
                    "picture": {
                        "tiny_url": "https://experiences/029d.tiny.jpg",
                        "small_url": "https://experiences/029d.small.jpg",
                        "medium_url": "https://experiences/029d.medium.jpg",
                    },
                    "is_me": false,
                },
                "is_mine": false,
                "is_saved": false,
                "saves_count": 32
            }
        ],
    "next_url": "https://base_url/experiences/?mine=false&saved=false&limit=2&offset=2"
}
```

### `GET /experiences/search?word=culture&latitude=8.5&longitude=-9.4&limit=20`
_Request:_
This endpoint is used to search experiences by `word` text.
You can also (optionally) specify a latitude and longitude to a located search.
You can also define a `limit` to let server know
how many elements you do want on each page
(if you skip this param server will return 20).

It searches between experiences and scenes titles and descriptions,
boosted by proximity (calculated with center points of an experience scenes)
and `saves_count`.

_Response:_
```json
{
    "results":
        [
            {
                "id": "3",
                "title": "Magic Castle of Culture",
                "description": "Don't even try to go there!",
                "picture": null,
                "author_profile": {
                    "username": "da_usr",
                    "bio": "about me",
                    "picture": null,
                    "is_me": true,
                },
                "is_mine": false,
                "is_saved": false,
                "saves_count": 5
            },
            {
                "id": "2",
                "title": "Baboon",
                "description": "Culture place...",
                "picture": {
                    "small_url": "https://experiences/8c29.small.jpg",
                    "medium_url": "https://experiences/8c29.medium.jpg",
                    "large_url": "https://experiences/8c29.large.jpg",
                },
                "author_profile": {
                    "username": "usr.nam",
                    "bio": "user info",
                    "picture": {
                        "tiny_url": "https://experiences/029d.tiny.jpg",
                        "small_url": "https://experiences/029d.small.jpg",
                        "medium_url": "https://experiences/029d.medium.jpg",
                    },
                    "is_me": false,
                },
                "is_mine": false,
                "is_saved": false,
                "saves_count": 32
            }
        ],
    "next_url": "https://base_url/experiences/search?word=culture&latitude=8.5&longitude=-9.4&limit=2&offset=2"
}
```

### `POST /experiences`

_Request(application/x-www-form-urlencoded):_
```json
{
    "title": "My travel",
    "description": "and other adventures",
}
```

_Response:_

_201_
```json
{
    "id": "8",
    "title": "My travel",
    "description": "and other adventures",
    "picture": null,
    "author_profile": {
        "username": "usr.nam",
        "bio": "user info",
        "picture": {
            "tiny_url": "https://experiences/029d.tiny.jpg",
            "small_url": "https://experiences/029d.small.jpg",
            "medium_url": "https://experiences/029d.medium.jpg",
        },
        "is_me": true,
    },
    "is_mine": true,
    "is_saved": false,
    "saves_count": 2
}
```

_422_
```json
{
    "error": {
        "source": "title",
        "code": "empty_attribute",
        "message": "Title cannot be empty"
    }
}
```


### `GET /experiences/<experience_id>`

Simple endpoint to fetch single experience by id.

_Response:_

_200_
```json
{
    "id": "8",
    "title": "MainSquare",
    "description": "A new description",
    "picture": null,
    "author_profile": {
        "username": "usr.nam",
        "bio": "user info",
        "picture": {
            "tiny_url": "https://experiences/029d.tiny.jpg",
            "small_url": "https://experiences/029d.small.jpg",
            "medium_url": "https://experiences/029d.medium.jpg",
        },
        "is_me": true,
    },
    "is_mine": true,
    "is_saved": false,
    "saves_count": 8
}
```


### `PATCH /experiences/<experience_id>`

_Request(application/x-www-form-urlencoded):_
```json
{
    "title": "",
    "description": "A new description",
}
```
It is also allowed to not define some fields
(if defined blank value will be set to blank).

_Response:_

_200_
```json
{
    "id": "8",
    "title": "MainSquare",
    "description": "A new description",
    "picture": null,
    "author_profile": {
        "username": "usr.nam",
        "bio": "user info",
        "picture": {
            "tiny_url": "https://experiences/029d.tiny.jpg",
            "small_url": "https://experiences/029d.small.jpg",
            "medium_url": "https://experiences/029d.medium.jpg",
        },
        "is_me": true,
    },
    "is_mine": true,
    "is_saved": false,
    "saves_count": 8
}
```

_404_
```json
{
    "error": {
        "source": "entity",
        "code": "not_found",
        "message": "Entity not found"
    }
}
```

_422_
```json
{
    "error": {
        "source": "title",
        "code": "wrong_size",
        "message": "Title must be between 1 and 30 chars"
    }
}
```


### `GET /experiences/<experience_id>/share-url`

This endpoint is used to retrieve a unique identified public experience link,
that must be captured by application to show its content.

_Response:_

_200_
```json
{
    "share_url": "pachatary.com/e/Ab3De6gH",
}
```


### `GET /experiences/<experience_share_id>/id`

This endpoint is to translate an experience public identifier share_id
(see previous endpoint) to internal id.
It must be used when receiving intent from external experience url
before making normal endpoint usage with ids.

_Response:_

_200_
```json
{
    "experience_id": "87",
}
```




### `POST /experiences/<experience_id>/save/`

Endpoint to save experience as favourite.

_Response:_

_201_

### `DELETE /experiences/<experience_id>/save/`

Endpoint to unsave experience as favourite.

_Response:_

_204_


### `POST /experiences/<experience_id>/picture/`

_Request(multipart/form-data):_

Param name to send the file: `picture`

_Response:_

_200_
```json
{
    "id": "8",
    "title": "My travel",
    "description": "and other adventures",
    "picture": {
        "small_url": "https://scenes/37d6.small.jpeg",
        "medium_url": "https://scenes/37d6.medium.jpeg",
        "large_url": "https://scenes/37d6.large.jpeg"
    },
    "author_profile": {
        "username": "usr.nam",
        "bio": "user info",
        "picture": {
            "tiny_url": "https://experiences/029d.tiny.jpg",
            "small_url": "https://experiences/029d.small.jpg",
            "medium_url": "https://experiences/029d.medium.jpg",
        },
        "is_me": true,
    },
    "is_mine": true,
    "is_saved": false
}
```

### `GET /scenes/?experience=<experience_id>`

_Response:_
```json
[
    {
        "id": "5",
        "title": "Plaça Mundial",
        "description": "World wide square!",
        "picture": {
            "small_url": "https://scenes/37d6.small.jpeg",
            "medium_url": "https://scenes/37d6.medium.jpeg",
            "large_url": "https://scenes/37d6.large.jpeg"
        },
        "latitude": 1.000000,
        "longitude": 2.000000,
        "experience_id": "5"
    },
    {
        "id": "4",
        "title": "I've been here",
        "description": "",
        "picture": null,
        "latitude": 0.000000,
        "longitude": 1.000000,
        "experience_id": "5"
    },
]
```

### `POST /scenes`

_Request(application/x-www-form-urlencoded):_
```json
{
    "title": "Plaça Major",
    "description": "The main square",
    "latitude": 1.2,
    "longitude": 0.3,
    "experience_id": "3"
}
```

_Response:_

_201_
```json
{
    "id": "8",
    "title": "Plaça Major",
    "description": "The main square",
    "picture": null,
    "latitude": 1.2,
    "longitude": 0.3,
    "experience_id": "3"
}
```

_422_
```json
{
    "error": {
        "source": "title",
        "code": "empty_attribute",
        "message": "Title cannot be empty"
    }
}
```

### `PATCH /scenes/<scene_id>`

_Request(application/x-www-form-urlencoded):_
```json
{
    "title": "",
    "description": "A new description",
    "latitude": -0.3,
    "longitude": 0.56,
}
```
It is also allowed to not define some fields
(if defined blank value will be set to blank).

_Response:_

_200_
```json
{
    "id": "8",
    "title": "MainSquare",
    "description": "A new description",
    "picture": null,
    "latitude": 1.2,
    "longitude": 0.56,
    "experience_id": "3"
}
```

_404_
```json
{
    "error": {
        "source": "entity",
        "code": "not_found",
        "message": "Entity not found"
    }
}
```

_422_
```json
{
    "error": {
        "source": "title",
        "code": "wrong_size",
        "message": "Title must be between 1 and 30 chars"
    }
}
```



### `POST /scenes/<scene_id>/picture/`

_Request(multipart/form-data):_

Param name to send the file: `picture`

_Response:_

_200_
```json
{
    "id": "8",
    "title": "Plaça Major",
    "description": "The main square",
    "picture": {
        "small_url": "https://scenes/37d6.small.jpeg",
        "medium_url": "https://scenes/37d6.medium.jpeg",
        "large_url": "https://scenes/37d6.large.jpeg"
    },
    "latitude": 1.2,
    "longitude": 0.3,
    "experience_id": "3"
}
```

### `POST /people/`

This endpoint is to create a `person` instance.
This `person` will be anonymous guest (until registration)
and has limited permissions (basically get information).
The response of this endpoint will be `auth_token` credentials,
composed by `access_token` and `refresh_token`,
that have to be persisted on the client.

_Request(application/x-www-form-urlencoded):_
```json
{
    "client_secret_key": "XXXX",
}
```

_Response:_

_201_
```json
{
    "access_token": "A_T_12345",
    "refresh_token": "R_T_67890",
}
```

### `PATCH /people/me`

This endpoint is to register a guest `person`.
Username and email is required.
`person` status change to registered
but will not have full permissions until email confirmation
(an email is sent with confirmation token).

_Request(application/x-www-form-urlencoded):_

_(http headers)_

`Authorization: Token ABXZ` (previous endpoint `access_token` response)

```json
{
    "username": "user.name",
    "email": "email@example.com"
}
```

_Response:_

_200_
```json
{
    "is_registered": true,
    "username": "user.name",
    "email": "email@example.com",
    "is_email_confirmed": false
}
```

### `POST /people/me/email-confirmation`

This endpoint is to confirm email and finish `person` register.
On previous endpoint, an email is sent with a confirmation token.
That token has to be sent as parameter.

_Request(application/x-www-form-urlencoded):_

_(http headers)_

`Authorization: Token ABXZ`

```json
{
    "confirmation_token": "C_T_ABXZ",
}
```

_Response:_

_200_
```json
{
    "is_registered": true,
    "username": "user.name",
    "email": "email@example.com",
    "is_email_confirmed": true
}
```

### `GET /people/me/email-confirmation/redirect?token=ABXZ`

This endpoint is to let Android app catch url to get the token and
call the previous endpoint, or if the user opens this link with a browser,
it redirects to 'app://pachatary.com/...' to force open deeplink
(both urls must be defined on Android app).

_Request:_

`token` as query param.

_Response:_

_304_

Location: 'app://pachatary.com/people/me/email-confirmation?token=ABXZ'

### `POST /people/me/login-email`

This endpoint is used to ask login email.
An email will be sent with an authenticated (using a token) link to login.

_Request(application/x-www-form-urlencoded):_

```json
{
    "email": "my@email.com",
}
```

_Response:_

_204_


### `GET /people/me/login/redirect?token=ABXZ`

This endpoint is to let Android app catch url to get the token and
call the previous endpoint, or if the user opens this link with a browser,
it redirects to 'app://pachatary.com/...' to force open deeplink
(both urls must be defined on Android app).

_Request:_

`token` as query param.

_Response:_

_304_

Location: 'app://pachatary.com/people/me/login?token=ABXZ'

### `POST /people/me/login`

This endpoint is to finish `person` login.
On previous endpoint, an email is sent with a login token.
That token has to be sent as parameter.

_Request(application/x-www-form-urlencoded):_

```json
{
    "token": "L_T_ABXZ",
}
```

_Response:_

_200_
```json
{
    "person": {
        "is_registered": true,
        "username": "user.name",
        "email": "email@example.com",
        "is_email_confirmed": true
    },
    "auth_token" : {
        "access_token": "A_T_12345",
        "refresh_token": "R_T_67890",
    }
}
```

### `GET /client-versions`

To check if client version has to be upgraded.

_Response:_

_200_
```json
{
    "android": {
        "min_version": 3
    }
}
```



### `GET /profiles/<username>`
### `GET /profiles/self`

Simple endpoint to fetch profile by username.

_Response:_

_200_
```json
{
    "username": "usr.nm",
    "bio": "This is my account",
    "picture": {
        "medium_url": "https://experiences/8c29.medium.jpg",
        "small_url": "https://experiences/8c29.small.jpg",
        "tiny_url": "https://experiences/8c29.tiny.jpg"
    },
    "is_me": false,
}
```


### `PATCH /profiles/self`

Endpoint to edit your own bio.

_Request(application/x-www-form-urlencoded):_
```json
{
    "bio": "A new description of myself",
}
```

_Response:_

_200_
```json
{
    "username": "usr.nm",
    "bio": "A new description of myself",
    "picture": {
        "medium_url": "https://experiences/8c29.medium.jpg",
        "small_url": "https://experiences/8c29.small.jpg",
        "tiny_url": "https://experiences/8c29.tiny.jpg"
    },
    "is_me": true,
}
```

_422_
```json
{
    "error": {
        "source": "bio",
        "code": "wrong_size",
        "message": "Bio can not be longer than 140 chars"
    }
}
```

### `POST /profiles/self/picture`

_Request(multipart/form-data):_

Param name to send the file: `picture`

_Response:_

_200_
```json
{
    "username": "usr.nm",
    "bio": "A new description of myself",
    "picture": {
        "medium_url": "https://experiences/8c29.medium.jpg",
        "small_url": "https://experiences/8c29.small.jpg",
        "tiny_url": "https://experiences/8c29.tiny.jpg"
    },
    "is_me": true,
}
```



## Documentation

This project has been developed using Django framework,
with Postgres as database and S3 as storage service.
Elasticsearch is used as search enginee.

Code structure follows a Clean Architecture approach
([explained in detail here](http://jordifierro.com/django-clean-architecture)),
emphasizing on code readability, responsibility decoupling
and unit testing.

Authentication part is a little bit custom (to better fit requirements and also with learning purposes).
It doesn't uses Django `User` model nor django-rest-framework, everything is handmade
(everything but cryptography, obviously :) ) and framework untied.
Special things are described here:
* There is anonymous guest user status. That allow users to enter to the app without register
but we can track and analyze them. That also helps making app more secure because
calls are made from guest users but authenticated and we can also control the number of registrations.
* There is no password. Guest user can register just with username and email,
which makes registration process easier. Login will be implemented using token validation via email.
* User is called person. Developer tends to treat a user like a model or a number,
`person` naming aims to remember who is really behind the screen.


## Setup

Follow these instructions to start working locally on the project:

* Download code cloning this repo:
```bash
git clone https://github.com/jordifierro/pachatary-api.git
```
* Install postgres and run:
```bash
./pachatary/setup/postgres.sh
```
to create user and database.
* Run postgres:
```bash
postgres -D /usr/local/var/postgres &
```
* Download elasticsearch-6.2.4, extract it inside `../env` folder
and then run:
```bash
../env/elasticsearch-6.2.4/bin/elasticsearch &
```
* Download redis-4.0.10, extract it inside `../env` folder
and then run:
```bash
../env/redis-4.0.10/src/redis-server &
```
* Install python version specified on `runtime.txt`
and run:
```bash
virtualenv -p `which python3.7` ../env
```
* Add this to the end of `../env/bin/activate` file:
```bash
source pachatary/setup/envvars.sh
```
* Get into the environment:
```bash
source ../env/bin/activate
```
and install dependencies:
```bash
pip install -r requirements.txt
```
* Migrate database:
```bash
python manage.py migrate
```
* Create django admin super user:
```bash
python manage.py createsuperuser
```
* Finally, you should be able to run unit and integration tests:
```bash
pytest                # python tests
python manage.py test # django tests
```

Once we have made the first time setup,
we can start everything up running:
```bash
source pachatary/setup/startup.sh
```
