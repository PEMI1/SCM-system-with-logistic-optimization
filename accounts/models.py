from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point


#base user manager allows you to edit the way user and superuser is created
#by default to create super user only email, username, and password are asked but now it will also ask for first and last name
class UserManager(BaseUserManager):  # never contains any field, only contains methods to create normal and super user
    def create_user(self, first_name, last_name, username, email, password=None):
        #Basic checks
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User must have an username')

        #create custom user that will have email, username, first and last name
        user = self.model(
            email = self.normalize_email(email), #convert email to lowercase if it has upercase letter
            username= username,
            first_name = first_name,
            last_name = last_name,
        )
        user.set_password(password)  # must set password for the user 
        user.save(using=self._db)  # takes db defined in setting and store this user there
        return user
    
    def create_superuser(self,first_name, last_name, username, email, password=None):
        # to create superuser first it must be normal user and then we will assign him as superuser
        user = self.create_user(
            email = self.normalize_email(email),
            username= username,
            password= password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin= True
        user.is_active=True
        user.is_staff =True
        user.is_superadmin = True
        user.save(using=self._db)
        return user

#by extending the AbstractBaseUser we are now customizing the user model and also django authentication function
class User(AbstractBaseUser): # this class will contain fields and methods
    VENDOR = 1
    CUSTOMER = 2
    SHIPPER = 3
    ROLE_CHOICE =(
        (VENDOR, 'Vendor'),
        (CUSTOMER, 'Customer'),
        (SHIPPER, 'Shipper'),

    )

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=12, blank=True)
    role= models.PositiveSmallIntegerField(choices=ROLE_CHOICE, blank=True, null=True)

    #required fields
    date_joined= models.DateTimeField(auto_now_add=True)
    last_login= models.DateTimeField(auto_now_add=True)
    created_date= models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_admin= models.BooleanField(default=False)
    is_staff= models.BooleanField(default=False)
    is_active= models.BooleanField(default=False)
    is_superadmin= models.BooleanField(default=False)

    USERNAME_FIELD = 'email'  #by default username field is used for login but we use email
    REQUIRED_FIELDS = ['username', 'first_name','last_name']  # email is already a required field

    objects = UserManager()  # teeling this user class to use the above user manager

    def __str__(self):
        return self.email  # string representation of this model
    
    def has_perm(self, perm, ob=None):  # only returns true if user is admin
        return self.is_admin
    
    def has_module_perms(self, app_label):  # only returns true if user is superuser so this model is only accessed by admin and superuser
        return True

    #custom function responsible to tell if user is Vendor or Customer 
    #above we have defined 'role' field of 'User' model to be either of 2 constants: 1/2
    #So this role is checked and accordingly user_role is assigned Vendor or Customer 
    #this user_role is returned when get_role function is called by Dashboard.html
    def get_role(self):  # here self mean user/object of User clas
        if self.role == 1:
            user_role = 'Vendor'
        elif self.role == 2:
            user_role = 'Customer'
        elif self.role == 3:
            user_role = 'Shipper'
        return user_role


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='users/profile_pictures', blank=True, null=True)
    cover_photo= models.ImageField(upload_to='users/cover_photos', blank=True, null=True)

    address = models.CharField(max_length=250, blank=True, null=True)
    location = models.PointField(geography=True, srid=4326)
    objects = models.Manager()

    country = models.CharField(max_length=15, blank=True, null=True)
    state = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=15, blank=True, null=True)
    pin_code = models.CharField(max_length=6, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(auto_now=True)

    # def full_address(self):
    #     return f'{self.address_line_1}, {self.address_line_2}'

    def __str__(self):
        return self.user.email


#table to store geospatial info of nepal
class LocalAddress(models.Model):
    province = models.IntegerField()
    district = models.CharField(max_length=50)
    unit_type = models.CharField(max_length=50)
    unit_name = models.CharField(max_length=50)
    district_c = models.IntegerField()
    shape_leng = models.FloatField()
    shape_area = models.FloatField()
    geom = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return self.district

    class Meta:
        verbose_name_plural = "Local addresses"


class Counties(models.Model):
    counties = models.CharField(max_length=25)
    codes = models.IntegerField()
    cty_code = models.CharField(max_length=24)
    dis = models.IntegerField(null=True)
    geom = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return self.counties

