from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver

from .models import User, UserProfile

#receives inputs from the sender/model(User) and sends to profile creater
#post_save signals when something is saved 
#pre_save signals when something is going to be saved
#kwargs- keyword arguments
#created flag returns true when a profile/user/object is created 
@receiver(post_save, sender=User)  #connect receiver with sender
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    # post_save.connect(post_save_create_profile_receiver,sender=User)
    print(created)
    #3 cases 
    #1.Fresh user is created(=True)..userProfile of the user is created
    #2.Existing user is updated(created=False)..userProfile of the user is also updated
    #3.UserProfile is deleted and this user is updated(created=False but in try, UserProfile class is trying to get unexisting profile of the user)...hence new profile is created with updated user info
    if created:
        #now create user profile
        UserProfile.objects.create(user=instance)
        print("user profile is created")
    else:
        try:
            profile=UserProfile.objects.get(user=instance)
            profile.save()
        except:
            #create the userprofile if not exist
            UserProfile.objects.create(user=instance)
            print("profile was not available but I created one")
           
        print("user is updated")

@receiver(pre_save,sender=User)
def pre_save_profile_receiver(sender, instance, **kwargs):#pre_save will not take created flag
    print(instance.username,'this user is being saved...So pre_save will run before post_save')