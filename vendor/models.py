from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notification

class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50 )
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)  # this is true when user registers and activates their account and finally admin approves their license
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name

    # to make the vendor approved Vendor will change is_approved to true and press save at the admin pannel. Whenever this happens We have to call django's inbuilt function 'save' and send approval mail to vendor.
    # args and kwargs are used when you don't know how many arguments u are going to pass
    def save(self, *args, **kwargs):
        # first check if the vendor has registered and its object has been created ie.vendor has a pk
        if self.pk is not None:
            #then update the existing vendor
            orig = Vendor.objects.get(pk=self.pk)  #get the original vendor obj
    

            #check if the is_approved checkbox has changed..we will send email only when it is changed
            if orig.is_approved != self.is_approved:  # since the vendor has not been saved yet(we are doing this process b4 saving the vendor), the original vendor(original status of the checkbox) will have false is_approved and the self vendor(current status of the checkbox) will have true is_approved
                mail_template = 'accounts/emails/admin_approval_email.html'
                context = {
                    'user' : self.user,
                    'is_approved' : self.is_approved,
                }
                
                if self.is_approved == True:
                    #Send notification email of successful approval
                    mail_subject = 'Congratulations! Your restaurant has been approved'
                    
                    send_notification(mail_subject, mail_template, context)
                else:
                    #Suppose the admin has changed is_active status from true to false in such case this else block will be trigered
                    #Send notification email of unsuccessful approval. Since the checkbox status did not changed, admin did not approve
                    mail_subject = 'We are sorry, you are not eligible for publishing your food menu on our marketplace'
                
                    send_notification(mail_subject, mail_template, context)

        #super allows us to access the save function of the Vendor class
        return super(Vendor,self).save(*args,*kwargs)