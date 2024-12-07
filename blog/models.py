from django.db import models


class Blog(models.Model):
    blogName = models.TextField(max_length=50 )
    common_prompt = models.TextField(max_length=2024 ,default="")
    common_promo = models.TextField(max_length=2024,default="" )
    runway_api = models.TextField(max_length=100,default='')        
    cloud_config = models.TextField(max_length=100,default='')    
    openai_api = models.TextField(max_length=100,default='')
    form4_submitted=models.BooleanField(default=False)    


class Urls(models.Model):
    url = models.TextField(max_length=2048)
    blog = models.ForeignKey(Blog,on_delete=models.CASCADE)

class Social_Media(models.Model):
    social = models.TextField(max_length=2048)
    blog = models.ForeignKey(Blog,on_delete=models.CASCADE)

class Dynamic_Field(models.Model):
    field = models.TextField(max_length=250)
    value = models.TextField(max_length=250)
    blog = models.ForeignKey(Blog,on_delete=models.CASCADE)

class Posting_Schedule(models.Model):
    blog = models.ForeignKey(Blog,on_delete=models.CASCADE)
    posting_time = models.DateTimeField()
    posting_day = models.TextField(max_length=20)
    promo_msg = models.TextField(max_length=2024,default='')
    gpt_prompt = models.TextField(max_length=2024,default='')
    language = models.TextField(max_length=200,default='English')
    content_type=models.TextField(max_length=10, default="")
    story_idea  = models.TextField(max_length=2024,default="")
    storyline=models.TextField(max_length=10000, default="")
    
    hook_scene=models.TextField(max_length=1000,default='')
    last_scene=models.TextField(max_length=1000,default='')
    
    hook_script=models.TextField(max_length=1000,default='')
    last_script=models.TextField(max_length=1000,default='')
    
    hook_dalle=models.TextField(max_length=1000,default='')
    last_dalle=models.TextField(max_length=1000,default='')
    
    hook_ssml=models.TextField(max_length=1000,default='')
    last_ssml=models.TextField(max_length=1000,default='')

    hook_animation_instructions=models.TextField(max_length=1000,default='')
    last_animation_instructions=models.TextField(max_length=1000,default='')

    posting_time_passed = models.BooleanField(default=False)
    


class Category(models.Model):
    posting_schedule = models.ForeignKey(Posting_Schedule,on_delete=models.CASCADE)
    category = models.TextField(max_length=100)

class Keyword(models.Model):
    posting_schedule = models.ForeignKey(Posting_Schedule,on_delete=models.CASCADE)
    keyword = models.TextField(max_length=100)

class Scene(models.Model):
    posting_schedule = models.ForeignKey(Posting_Schedule,on_delete=models.CASCADE)
    script= models.TextField(max_length=2048,default="")
    scene = models.TextField(max_length=2048,default="")
    ssml= models.TextField(max_length=2048,default="")
    animation_instruction= models.TextField(max_length=2048,default="")
    dalle_prompt=models.TextField(max_length=2048,default="")

    

