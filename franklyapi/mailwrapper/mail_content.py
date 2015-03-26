dict = {

    "forgot_password": {

                          "subject": "Forgot your password?",
                          "body": '''Let's get you asking again. You can reset your password by clicking on the link below.
                                      <br><br>
                                    <a href={reset_password_link}>{reset_password_link}</a>
                                    <br><br>
                                    This link will expire in 48 hrs. If you did not request a password reset, Please ignore this mail.
                                  '''


                        },
    "welcome_mail":   {
                          "subject" : "Welcome to Frankly.me!",
                          "body": '''Welcome to Frankly.me where Arvind Kejriwal,Javed Akhtar, Gurdaas Maan,Yogendra Yadav and \n
                                      many more are waiting for you. <br/><br/>Frankly.me is now here to help you reach the\n
                                      most important people of your life.Just log in, ask frank questions and get\n
                                      answered in form of video selfie. <br/><br/>  Just in case you forget, your credentials are as follows: <br/>\n
                                      Username: %s <br/> Password: %s <br/><br/>\n
                                      Have a rocking stay at Frankly.me!''',
                        },
    "question_asked": {
                          "subject" : "Your question has been asked",

                          "body": '''Congratulations!<br/><br/>Your question has been successfully posted.We will make sure it gets answered and till then, you can ask more questions to
                                    %s. <br/><br/> Also, don't forget to answer the questions that you are asked by your
                                    fans and friends. They might be waiting for you to respond.''',

                          "body_first_question": "Your first question has been asked. We will try our best to get it answered.<br/><br/>"
                                  "Go ahead and ask more questions to your favorite celebrities. We will notify you"
                                  " once your question"
                                  " has been answered."

                        },
    "question_answered": {
                          "subject" : "Your question has been answered!",
                          "body": '''%s has answered your question <a href='%s'>"%s"</a>. Check it out now!'''

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

                        },
    "sapru"            : {
        "subject" : " Win an Indian Jersey on Frankly.me!",

                         "body" : '''
                                     You have just asked a question from Jatin Sapru on FranklyMe <br/><br//>
                                     %s <br/> <br/>
                                     You've now officially entered the <b>#WinIndiaJersey</b> contest! <br/><br/>
                                     The users with the top most up-voted questions get a chance to win an authentic Indian jersey signed by <b>Kapil Dev, VVS Laxman, Murali Kartik,</b> etc.
                                     Just get your question up-voted by your friends and family to win your own Indian jersey and support Team India this Cricket World Cup!
                                     <br/><br/>For any other information, write to us at hi@frankly.me .'''
                        }
}