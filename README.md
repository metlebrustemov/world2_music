# World2Music

Bulud musiqi paylasim platformu.    
Web url: [W2Music](https://w2music.herokuapp.com)     
    
## World2Music RestAPI    
    
Base Url Address: https://w2music.herokuapp.com     
     
### Register Request
     
POST /api/u   
*Required parameters*    
     
>**user_name** - Alphanumeric unical string[a-z][A-Z][0-9].     
>**user_email** - Valid email address.    
>**user_pass** - A secure password.     
  
*Returned data*    
>Success or error message including json response     
  
### Login Request  
  
GET /api/u            
*Required parameters*   

>**user_email** - Email used when signing up.     
>**user_pass** - Password used when signing up.        
  
*Returned data*
>Success or error message including json response.      
>          
>If login is successful:      
>**token** - It will be used in all transactions. It must be well protected.    
   
### Get Media (one or all) Request   
   
GET /api/m  
*Required parameters*   

>**user_email** - Name used when signing up.     
>**u_token** - User token.      
>**m_token** - Media token (optional).      
  
*Returned data*
>Success or error message including json response.      
>          
>If request is successful:      
>If the **m_token**  has been sent:   
>Media information associated with m_token like json   
>Else:    
>m_token information for all accessible media like json   


### Create New Media Request   
   
POST /api/m  
*Required parameters*   

>**user_email** - Name used when signing up.     
>**u_token** - User token.      
>**music_name** - Media name.      
>**music_author** - Media author name.   
>**music_is_public** - True or False (optional).      
>**music_file** - Media file (embed to POST request).      
  
*Returned data*
>Success or error message including json response.      
>          
>If request is successful:      
>**m_token** - New media token   
  

### Update Media Request   
   
PATCH /api/m  
*Required parameters*   

>**user_email** - Name used when signing up.     
>**u_token** - User token.      
>**music_name** - Media new name.      
>**music_author** - Media new author name.      
>**music_is_public** - True or False.      
  
*Returned data*
>Success or error message including json response.      
>          
>If request is successful:      
>**m_token** -Updated media token   
   
  
   
### Delete Media Request   
   
PATCH /api/m  
*Required parameters*   

>**user_email** - Name used when signing up.     
>**u_token** - User token.      
>**m_token** - Media token.      
  
*Returned data*
>Success or error message including json response.      

