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
                          "body": '''Welcome to Frankly.me where Arvind Kejriwal, Javed Akhtar, Gurdaas Maan, Yogendra Yadav and \n
                                      many more are waiting for you. <br/><br/>Frankly.me is now here to help you reach the\n
                                      most important people of your life. Just log in, ask frank questions and get\n
                                      answered in form of video selfie. <br/><br/> Just in case you forget,
                                      your credentials are as follows: <br/>\n
                                      Username: %s <br/> Password: %s <br/><br/>\n
                                      Have a rocking stay at Frankly.me!''',
                        },
    "question_asked_by": {
                          "subject" : "Your question has been asked",

                          "body": '''Congratulations!<br/><br/>Your question has been successfully posted. We will make
                                     sure it gets answered and till then, you can ask more questions to
                                     %s. <br/><br/> Also, don't forget to answer the questions that you are asked by your
                                     fans and friends. They might be waiting for you to respond.''',

                          "body_first_question": '''Your first question has been asked. We will try our best to get it
                                                    answered.<br/><br/> Go ahead and ask more questions to your favorite
                                                    celebrities. We will notify you once your question has been answered
                                                    .'''

                        },
    "question_asked_to": {
                          "subject": "%s just asked you a question!",
                          "body": '''%s has just asked you "%s". <br/><br/> Answer this and other interesting questions
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

