from django.shortcuts import render,redirect
from .models import *

from django.core.files import File
# Create your views here.

# #####################  functions of the project ######################
# modules
import cv2
import numpy as np
from pydub import AudioSegment
import pydub
import math as mt
from PIL import Image,ImageStat


def converter(audio_path,path,name):
    from moviepy.editor import VideoFileClip, AudioFileClip
    # Open the video and audio
    try:
        video_clip = VideoFileClip(path)
        audio_clip = AudioFileClip(audio_path)

        # Concatenate the video clip with the audio clip
        final_clip = video_clip.set_audio(audio_clip)

        # Export the final video with audio
        mixed_path='./media/temp_videos/'+name+".mp4"
        final_clip.write_videofile(mixed_path)
        return True,mixed_path
    except:
        False,'aaa'



def give_brightness( im_file ):
    im = Image.fromarray(im_file)
    stat = ImageStat.Stat(im)
    r,g,b = stat.rms
    return mt.sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2))

def map_brightness_to_note(brightness):
    # Map the brightness value to a musical note (adjust these mappings as needed)
    # Here, we're using a simple linear mapping
    min_brightness = 0  # Adjust as needed based on your video content
    max_brightness = 255
    min_note_freq = 50  # Adjust the starting frequency as needed
    max_note_freq = 500  # Adjust the ending frequency as needed
    mapped_freq = np.interp(brightness, [min_brightness, max_brightness], [min_note_freq, max_note_freq])
    return mapped_freq

def generate_sine_wave(frequency, duration, volume, sample_rate=44100):
    # Generate array with time values
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    # Generate a sine wave
    sine_wave = np.sin(frequency * t * 2 * np.pi)

    # Ensure that highest value is in 16-bit range
    audio = sine_wave * (2**15 - 1) * volume

    # Convert to 16-bit data
    audio = audio.astype(np.int16)

    # Create audio segment
    audio_segment = AudioSegment(
        audio.tobytes(), 
        frame_rate=sample_rate,
        sample_width=audio.dtype.itemsize, 
        channels=1
    )

    return audio_segment

def generate(path,name):
    audio = AudioSegment.silent(duration=0)

    cap = cv2.VideoCapture(path)
    while True:
        ret, frame = cap.read()
        if not ret:
           break 

        img=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        # Calculate brightness (you can use other metrics as well)
        brightness = give_brightness(img)
        # Map brightness to audio frequency
        frequency = map_brightness_to_note(brightness)

        # Calculate the duration of each frame
        video_duration = cap.get(cv2.CAP_PROP_POS_MSEC) # Get the video duration in milliseconds
        frame_rate = cap.get(cv2.CAP_PROP_FPS) # Get the frame rate of the video
        frame_duration = 1000 / frame_rate # Calculate the duration of each frame in milliseconds

        # Generate a sine wave with the mapped frequency
        sine_wave = generate_sine_wave(frequency, frame_duration/1000, 1)
        

        # Append the audio segment with a short audio tone
        audio +=  sine_wave
        # AudioSegment.silent(duration=int(frame_duration))
        # Export the generated audio
        
    audio_path=f'./media/temp_audios/{name}.wav'
    audio.export(audio_path, format='wav')
    return audio_path





######################### end ##########################################

def home(request):
    if request.method=='GET':
        objs=Audio.objects.all()
        for o in objs:
            o.delete()
    
        objs=VideoAudio.objects.all()
        for o in objs:
            o.delete()

        objs=Video.objects.all()
        for o in objs:
            o.delete()

        context={} 
        return render(request,'home.html',context)
    else:
        # for post request
        f=request.FILES.get('xieauo',None)
        if f is not None:
            print(type(f),'  =file saved by django')
            video=Video.objects.create(vi_file=f)
            name=video.vi_file.name.split('/')[1].split('.')[0]  # actual name to be sent 
            # print(name)
            path='./media/'+video.vi_file.name  # actual path to be sent
            print(path,"  =file path")
            # actual functioning
            audio_path=generate(path,name)
            f=File(open(audio_path,'rb'))  # read as binary
            print(type(f)," =file saved by us")
            audio=Audio.objects.create(au_file=f)
            print('file saved peacefully using django')
            f.close()
            
            choice=request.POST['filter']
            if choice=='au':
                context={'audio':audio,'mssg':'1'}
                return render(request,'output.html',context)
            else:
                check,mixed_path=converter(audio_path,path,name)
                if check:
                    f=File(open(mixed_path,'rb'))  # read as binary
                    print(type(f)," =audio video file saved by us")
                    audiovideo=VideoAudio.objects.create(auvi_file=f)
                    print('file saved peacefully using django')
                    f.close()
                    context={'video':audiovideo,'mssg':'2'}
                    return render(request,'output.html',context)
                else:
                    redirect('home')
        else:
            return render(request,'output.html',{'mssg':'0'})
    
'''
mssg=1  then only audio
mssg=2 then audio + video
msssg=0 then file not accepted
'''