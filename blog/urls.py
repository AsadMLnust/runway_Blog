
from . views import *
from django.urls import path
urlpatterns = [

    path('', login_view, name='login_view'),
    path('home',index,name='index'),
    path('form2/<int:blog_id>',form2,name='form2'),
    path('form3/<int:blog_id>',form3,name='form3'),
    path('form4/<int:blog_id>',form4,name='form4'),
    path('generateStoryIdea',generateStoryIdea,name='generateStoryIdea'),
    path('finalizeIdeas',finalizeIdeas,name='finalizeIdeas'),
    path('form5/<int:blog_id>',form5,name='form5'),
    path('view_form5/<int:blog_id>',view_form5,name='view_form5'),
    path('edit_blogs', editblogs, name='previous_blogs'),  
]