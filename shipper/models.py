from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notification

class Shipper(models.Model):
    user = models.OneToOneField(User, related_name='s_user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='s_userprofile', on_delete=models.CASCADE)
    shipper_name = models.CharField(max_length=50 )
    shipper_slug = models.SlugField(max_length=100, unique=True)
    shipper_license = models.ImageField(upload_to='shipper/license')
    is_approved = models.BooleanField(default=False)  # this is true when user registers and activates their account and finally admin approves their license
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.shipper_name

    # to make the shipper approved shipper will change is_approved to true and press save at the admin pannel. Whenever this happens We have to call django's inbuilt function 'save' and send approval mail to shipper.
    # args and kwargs are used when you don't know how many arguments u are going to pass
    def save(self, *args, **kwargs):
        # first check if the shipper has registered and its object has been created ie.shipper has a pk
        if self.pk is not None:
            #then update the existing shipper
            orig = Shipper.objects.get(pk=self.pk)  #get the original shipper obj
    

            #check if the is_approved checkbox has changed..we will send email only when it is changed
            if orig.is_approved != self.is_approved:  # since the shipper has not been saved yet(we are doing this process b4 saving the shipper), the original shipper(original status of the checkbox) will have false is_approved and the self shipper(current status of the checkbox) will have true is_approved
                mail_template = 'accounts/emails/admin_approval_email.html'
                context = {
                    'user' : self.user,
                    'is_approved' : self.is_approved,
                    'to_email': self.user.email,
                }
                
                if self.is_approved == True:
                    #Send notification email of successful approval
                    mail_subject = 'Congratulations! Your business has been approved'
                    
                    send_notification(mail_subject, mail_template, context)
                else:
                    #Suppose the admin has changed is_active status from true to false in such case this else block will be trigered
                    #Send notification email of unsuccessful approval. Since the checkbox status did not changed, admin did not approve
                    mail_subject = 'We are sorry, you are not eligible for connecting your business with us'
                
                    send_notification(mail_subject, mail_template, context)

        #super allows us to access the save function of the shipper class
        return super(Shipper,self).save(*args,*kwargs)