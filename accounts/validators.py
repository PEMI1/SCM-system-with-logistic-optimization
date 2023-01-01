from django.core.exceptions import ValidationError
import os
#Custom validator function

#this overrides django default imageField error message
def allow_only_images_validator(value):
    ext = os.path.splitext(value.name)[1] # cover-image.jpg - 0 position is cover-image 1 position is .jpg
    print(ext)
    valid_extensions =  ['.png','.jpg', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Allowed extensions: ' +str(valid_extensions))