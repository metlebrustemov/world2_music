# World2Music
Bulud musiqi paylasim platformu.
Web url: [W2Music](https://w2music.herokuapp.com)
## World2Music RestAPI
Base Url Address: https://w2music.herokuapp.com

### Register Request
POST /api/u
Required parameters
>user_name - Alphanumeric unical string[a-z][A-Z][0-9]
>user_email - Valid email address
>user_pass - A secure password

Returned data
>Success or error message including json response

### Login Request
GET /api/u
Required parameters
>user_email - Name used when signing up
>user_pass - Password used when signing up

Returned data
>Success or error message including json response
>
>If login is successful:
>token - It will be used in all transactions. It must be well protected.