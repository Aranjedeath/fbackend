from configs import config

dict = {

    "forgot_password": {

                          "subject": "Forgot your password?",
                          "body": '''Let's get you asking again. You can reset your password by clicking on the link below.
                                      <br><br>
                                    <a href={reset_password_link}>{reset_password_link}</a>
                                    <br><br>
                                    This link will expire in 48 hrs. If you did not request a password reset,
                                    Please ignore this mail.
                                  '''


                        },
    "welcome_mail":   {
                          "subject" : "Welcome to Frankly.me!",
                          "body": '''Welcome to Frankly.me where public figures from all walks and forms of
                                    life give frank answers to your questions. <br/><br/>
                                    Also, we've just created your profile. You can use it to ask anybody anything or even
                                    answer questions of your friends and followers.<br/><br/> http://frankly.me/{0}
                                    <br/><br/>
                                    Have beautiful conversations at frankly.me
                                    '''
                        },
    "question_asked_by": {
                          "subject" : "Your question has been asked",

                          "body": '''Congratulations {0}, <br/><br/> Your question to {1} has been successfully posted.
                                     <br/><br/>You can view {2}'s complete profile and see his previous replies. <br/><br/>
                                     Also you can meet and start frank conversations with many other interesting people
                                     at frankly.me/discover''',

                          "body_first_question": '''Your first question has been asked. We will try our best to get it
                                                    answered.<br/><br/> Go ahead and ask more questions to your favorite
                                                    celebrities. We will notify you once your question has been answered
                                                    .'''

                        },
    "question_asked_to": {
                          "subject": "%s just asked you a question!",
                          "body": '''{0} has just asked you <a href="{1}">"{2}"</a>. <br/><br/> Answer this and other interesting questions
                                      on video through the Frankly android or iOS apps.'''

                         },
    "post_add": {
                          "subject" : "Your question has been answered!",
                          "body": '''%s has answered your question <a href='http://frankly.me/p/%s'>"%s"</a>. Check it out now!'''

                        },
    "new_celebrity_profile": {
                          "subject": "%s just joined frankly.me , Ask them anything",
                          "body":""
    },
    "inactive_profile" : {
                         "subject": "Howdy Rockstar! We are missing you!",
                         "body": '''Too busy at work? Or is it your beloved not letting you go? Or having more pressing issues?
                                    Must be one of those reasons, as we haven't heard from you for a long time. You
                                    have not used frankly.me for a while now and we are missing you.
                                    You must find some time to tag along with us, to answer questions which your
                                    friends and fans wanna know, and to ask questions from your role models and idols
                                    who are waiting for you to connect with them.
                                    If you have forgotten your credentials, we will be happy to help you with that. Reach
                                    us on app or website and we will help you retrieve them.
                                    We miss you and wish to hear from you more often...'''

                        }
}


mail_dict = {
    "logo_target_url": config.WEB_URL,
    "logo_image_url": config.LOGO_URL,
    "company_name": config.COMPANY_NAME,
    "pixel_image_url": config.PIXEL_IMAGE_ENDPOINT,
    "signature": "Pallavi, <br/> Community Manager <br/> Frankly.me",
    "team_signature": "Lots of love, <br/> Frankly.me Team"
}

