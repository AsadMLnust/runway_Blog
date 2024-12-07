from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate,login
from django.conf import settings
from django.contrib import messages
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel,Field
from langchain_core.prompts  import PromptTemplate
from django.utils.timezone import now

from dotenv import load_dotenv
load_dotenv()



from datetime import datetime, timedelta

def day_time_to_datetime(day, time):
    # Get the current date and time
    now = datetime.now()

    # Get the weekday index for the input day (0=Monday, 6=Sunday)
    day_index = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(day)

    # Calculate the target date for the input day
    current_weekday = now.weekday()  # Current weekday index
    days_difference = (day_index - current_weekday) % 7  # Adjust to the same week
    target_date = now + timedelta(days=days_difference)

    # Combine the target date with the time
    final_datetime = datetime.combine(target_date.date(), datetime.strptime(time, "%H:%M").time())

    # Check if the datetime has already passed
    if final_datetime < now:
        final_datetime += timedelta(days=7)  # Move to the next week

    return final_datetime


def login_view(request):
    print(request.method)
    if request.user.is_authenticated:
            return redirect("index")
            
    if request.method =='POST':

        try:
            username = request.POST['username']

            password = request.POST['password']
        except KeyError as e:
            messages.success(request, f"Missing {e}")
            return render( request, 'login.html' )
        try:
            user = User.objects.get(username=username)
        except:
            messages.success(request, "Invalid username")
            return render( request, 'login.html' )

        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request,user)
            return redirect("index")
        else:
            messages.success(request, "Invalid Credentials")
            return render( request, 'login.html' )
        

    return render( request, 'login.html' )



def index(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            blogName = request.POST['blogName']
            posting_day = request.POST.getlist('posting_day[]')
            posting_time = request.POST.getlist('posting_time[]')
            social_media = request.POST.getlist('social_media[]')
            extra_field = request.POST.getlist('extra_field[]') 
            extra_value = request.POST.getlist('extra_value[]') 

            urls = request.POST.getlist('urls[]')
            blog = Blog.objects.create(blogName = blogName) 
            blog.save()

            for s in social_media:
                social = Social_Media.objects.create(blog=blog,social=s)
                social.save()

            for u in urls:
                url = Urls.objects.create(blog=blog,url=u)
                url.save()

            for day,time in zip(posting_day,posting_time):
                date_time_time = day_time_to_datetime(day,time)
                print(time)
                ps = Posting_Schedule.objects.create(blog=blog,posting_day=day,posting_time= date_time_time)
                ps.save()

                
            for f,v in zip(extra_field,extra_value):
                dynamic_field = Dynamic_Field.objects.create(blog=blog,field=f,value= v)
                dynamic_field.save()


            return redirect('form2', blog_id=blog.id)

        
        return render( request, 'index.html' )
    else:
        return redirect('login_view')
    

def form2(request,blog_id:int):
    if request.user.is_authenticated:
        if request.method =='GET':
            try:
                blog = Blog.objects.get(id = blog_id)
            except:
                messages.success(request, "Blog Does not exist")
                return redirect("index")    
            return render(request,"form2.html",context={'blog':blog})
        
        if request.method =='POST':
            try:
                blog_id = request.POST['blog_id']
                blog = Blog.objects.get(id = blog_id)    
                common_prompt = request.POST['common_prompt']
                common_promo = request.POST['common_promo']
                blog.common_promo = common_promo
                blog.common_prompt = common_prompt
                blog.save()
                posting_schedules = Posting_Schedule.objects.filter(blog = blog) 
                print(posting_schedules)   
                for ps  in posting_schedules:

                    specific_promo = request.POST[f'specific_promo_{ps.id}']
                    specific_prompt = request.POST[f'specific_prompt_{ps.id}']
                    language = request.POST[f'language_{ps.id}']
                    print(f" Specific PROMO {specific_promo}")
                    ps.promo_msg = specific_promo
                    ps.gpt_prompt = specific_prompt
                    ps.language = language
                    ps.save()

                    categories = request.POST.getlist(f"categories_{ps.id}[]")
                    keywords = request.POST.getlist(f"keywords_{ps.id}[]")
                    Category.objects.filter(posting_schedule=ps).delete()
                    Keyword.objects.filter(posting_schedule=ps).delete()
                    print(keywords)
                    print(categories)

                    for k in keywords:
                        Keyword.objects.create(posting_schedule = ps,keyword = k ).save()

                    for c in categories:
                        Category.objects.create(posting_schedule = ps,category =c ).save()
                    
                return redirect('form3', blog_id=blog.id)
                
            except Blog.DoesNotExist:
                messages.success(request, "Blog Does not exist")
                return redirect("index")    
            except KeyError as e:
                messages.success(request, f"Invalid Input  missing {e}  ")
                return render(request,"form2.html",context={'blog':blog})
            




            return render(request,"form2.html",context={'blog':blog})
        

    return redirect ('login_view')
    

def form3(request,blog_id:int):
    if request.user.is_authenticated:
        if request.method == 'GET':
            try: 
                blog = Blog.objects.get(id = blog_id)
            except:
                messages.success(request,"Blog Does not exist")
                return redirect('index')

            return render(request,'form3.html',context={'blog':blog})
        if request.method == "POST":
            try:
                blog_id = request.POST['blog_id']
                blog = Blog.objects.get(id = blog_id)
                runway_api = request.POST['runway_api']
                cloud_config = request.POST['cloud']
                openai_api = request.POST['openai_api']

                blog.runway_api = runway_api
                blog.cloud_config  =cloud_config
                blog.openai_api = openai_api
                blog.save()
                return redirect('form4', blog_id=blog.id)



            except Blog.DoesNotExist:
                messages.success(request,"Blog Does not exist")
                return redirect('index')
            except KeyError as e:
                messages.success(request, f"Invalid Input  missing {e}  ")
                return render(request,"form3.html",context={'blog':blog})

    return redirect ('login_view')


def form4(request,blog_id:int):
    if request.user.is_authenticated:
        if request.method == 'GET':
            try: 
                blog = Blog.objects.get(id = blog_id)
            except:
                messages.success(request,"Blog Does not exist")
                return redirect('index')

            return render(request,'form4.html',context={'blog':blog})
        


def generateStoryIdea(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            posting_id = request.POST.get('posting_id')
            content_type = request.POST.get('contentType')
            posting_schedule = Posting_Schedule.objects.get(id=posting_id)
            posting_schedule.content_type = content_type
            posting_schedule.save()
            blog = posting_schedule.blog
            
            model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
            prompt = f"""Generate a story idea for a {posting_schedule.content_type} which is a part of blog series titled {blog.blogName}. The common prompt for this series is {blog.common_prompt}, the common promo message mesage for this series is {blog.common_promo}. 
For this specific Story use the prompt {posting_schedule.gpt_prompt} and the promo message {posting_schedule.promo_msg}.
The categories for this story Idea are as follows:
{"\n".join([cat.category for cat in Category.objects.filter(posting_schedule = posting_schedule)])}
The Targetted keywords for this story Idea are as follows:
{"\n".join([k.keyword for k in Keyword.objects.filter(posting_schedule = posting_schedule)])}
            """
            response = model.invoke(prompt)
            response = response.content.strip()
            
            return JsonResponse({"generated_idea": response})
        

def finalizeIdeas(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            
            try:
                blog_id=request.POST['blog_id']
                blog = Blog.objects.get(id = blog_id)
                posting_schedules = Posting_Schedule.objects.filter(blog = blog)
                for ps in posting_schedules:
                    idea = request.POST[f"gen_idea_{ps.id}"]
                    if idea.strip() == '':
                        # show error message that idea cannot be empty
                        pass
                    ps.story_idea = idea
                    ps.save()
                blog.form4_submitted = True
                blog.save()
                from threading import Thread
                Thread(target=form5,args = (request,blog_id)).start()
                return redirect('view_form5', blog_id=blog_id)
            except Blog.DoesNotExist:
                # error message and redirect to index
                return HttpResponse("blog does not exist") 
                pass
            except KeyError as e:
                return HttpResponse(f"Key error {e}") 
                pass
            

            pass


    pass



def form5(request,blog_id:int):
            print("\n\n\n\n\nSTARTED GENERATION\n\n\n")
            model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
            try:
                
                blog = Blog.objects.get(id = blog_id)
                posting_schedules = Posting_Schedule.objects.filter(blog = blog)

                for ps in posting_schedules:
                    print(f"started generation story idea for ps {ps.id}")

                    story_idea=ps.story_idea
                    prompt=f"""Generate a creative storyline for the story idea of: {story_idea}."""
                    storyline = model.invoke(prompt)
                    storyline = storyline.content.strip()
                    ps.storyline = storyline
                    ps.save()
                    print(f"generated story idea for ps {ps.id}")

                    prompt=f"""Generate a creative hook_scene for the storyline of: {storyline}."""
                    hook_scene = model.invoke(prompt)
                    hook_scene = hook_scene.content.strip()
                    ps.hook_scene = hook_scene
                    prompt=f"""Generate a creative last_scene for the storyline of: {storyline}."""
                    last_scene = model.invoke(prompt)
                    last_scene = last_scene.content.strip()
                    ps.last_scene = last_scene
                    ps.save()


                    hook_script = generate_script(hook_scene,model)
                    ps.hook_script = hook_script
                    
                    last_script = generate_script(last_scene,model)
                    ps.last_script = last_script
                    ps.save()

                    hook_dalle = generate_dalle(hook_script,model)
                    ps.hook_dalle = hook_dalle
                    ps.save()
                    last_dalle = generate_dalle(last_script,model)
                    ps.last_dalle = last_dalle
                    ps.save()
                    hook_ssml = generate_ssml(hook_script,model)
                    ps.hook_ssml = hook_ssml

                    last_ssml = generate_ssml(last_script,model)
                    ps.last_ssml = last_ssml

                    hook_animation = generate_animation_instructions(hook_dalle,model)
                    ps.hook_animation_instructions = hook_animation

                    last_animation = generate_animation_instructions(last_dalle,model)
                    ps.last_animation_instructions = last_animation
                    ps.save()
                    
                    
                    parser = JsonOutputParser(pydantic_object=Scene_List)
                    generate_scenes_prompt = PromptTemplate(
                    template =  """
                    Divide this story line into a list of scenes {storyline}
                    {format_instructions}
                    """,
                        input_variables=["storyline"],
                        partial_variables={"format_instructions": parser.get_format_instructions()},
                    )
                    
                    chain = generate_scenes_prompt | model | parser 
                    while 1:
                        try:
                            scenes =chain.invoke({"storyline":ps.storyline})['scene']
                            
                            break
                        except:
                            print("error generating scenes")
                            continue
                    print(scenes)
                    for scene in scenes:
                        s = Scene.objects.create(posting_schedule = ps)
                        print(scene)
                        s.scene = scene
                        s.script = generate_script(scene,model)
                        s.ssml = generate_ssml(s.script,model)
                        s.dalle_prompt = generate_dalle(s.script,model)
                        s.animation_instruction = generate_animation_instructions(s.dalle_prompt,model)
                        s.save()




            
            except:
                None


def view_form5(request,blog_id):
    blog = Blog.objects.get(id = blog_id)
    for ps in Posting_Schedule.objects.filter(blog = blog):
        if ps.posting_time  < now():
            ps.posting_time_passed = True
    return render(request,"form5.html",context={"blog":blog})
    pass
def generate_script(scene:str,model)->str:
    prompt=f"""Generate a script for the following scene: {scene}."""
    response = model.invoke(prompt)
    return response.content.strip()

def generate_ssml(script:str,model)->str:
    prompt=f"""Generate a SSML script for the following script: {script}."""
    response = model.invoke(prompt)
    return response.content.strip()

def generate_dalle(script:str,model)->str:
    prompt=f"""Generate a dalle prompt for following script: {script}."""
    response = model.invoke(prompt)
    return response.content.strip()

def generate_animation_instructions(dalle_prompt:str,model)->str:
    prompt=f"""Generate animation instructions for following dalle prompt: {dalle_prompt}."""
    response = model.invoke(prompt)
    return response.content.strip()


class Scene_List(BaseModel):
    scene:list[str] = Field(description="List of generated scenes")

def editblogs(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            user = request.user
            blogs = Blog.objects.all()
            return render(request, "edit.html",context={'blogs':blogs})