from transformers import AutoTokenizer, pipeline
from youtube_transcript_api import YouTubeTranscriptApi
import streamlit as st
from streamlit_player import st_player

@st.cache(allow_output_mutation = True)
def get_models():
  tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")

  summarizer = pipeline('summarization')
  return tokenizer, summarizer

tokenizer, summarizer = get_models()
def get_result(i):
  text_ids=ids[i:i+batch]
  text=tokenizer.decode(text_ids,temperature=1.5)
  if(len(text_ids)<142):
    max_length=50
    min_length=25
  else:
    min_length=60
    max_length=142
  res=summarizer(text,max_length=max_length,min_length=min_length)[0]
  return res['summary_text']

st.title("Youtube Video Summarization")
st.write('This is a web app where you can enter a youtube video link and get a summary of the video.')
selection = st.selectbox('You can enter your own youtube link or try on few samples : ',('Choose an option','Try on few sample videos','Enter your own video link'))

if selection == 'Try on few sample videos':
  youtube_video = st.selectbox('Few Examples:',('Choose an option','https://www.youtube.com/watch?v=Cu3R5it4cQs','https://www.youtube.com/watch?v=PZEQnCaGxgw','https://www.youtube.com/watch?v=TKXldNsmRaw'))
  if youtube_video == 'Choose an option':
    pass
  else:
    video_id = youtube_video.split("=")[1]
    state = st.text('\n Processing video, Please wait.....')
    progress_bar = st.progress(30)
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    result = ""
    for i in transcript:
        result += ' ' + i['text']

    result=result.strip()
    progress_bar.progress(50)
    ids=tokenizer(result)['input_ids']
    ids=ids[1:-1]

    if(len(ids)>2000):
      batch=1000
    elif(len(ids)>1000):
      batch=500
    else:
      batch=250

    progress_bar.progress(70)
    summarized_text=[get_result(i) for i in range(0,len(ids),batch)]

    summarized_text=[i.strip() for i in summarized_text]

    summarized_result='. '.join(summarized_text)
    summarized_result = summarized_result.replace('..', '.')
    progress_bar.progress(90)
    st.subheader('Submitted Youtube Video:')
    st_player(youtube_video)
    progress_bar.progress(100)
    st.subheader('Summarized Result:')
    st.write(summarized_result)
    progress_bar.empty()
    state.text('\n Completed!')

if selection == 'Enter your own video link':
  form = st.form(key="form")
  youtube_video = form.text_input("Enter the youtube link")
  predict_button = form.form_submit_button(label='Get Video Summary')
  #youtube_video = st.text_input('Enter the youtube link')

  if predict_button:
    if('youtube.com/watch' in youtube_video):
      video_id = youtube_video.split("=")[1]
      state = st.text('\n Processing video, Please wait.....')
      progress_bar = st.progress(30)
      try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        result = ""
        for i in transcript:
            result += ' ' + i['text']

        result=result.strip()
        progress_bar.progress(50)
        ids=tokenizer(result)['input_ids']
        ids=ids[1:-1]

        if(len(ids)>2000):
          batch=1000
        elif(len(ids)>1000):
          batch=500
        else:
          batch=250

        progress_bar.progress(70)
        summarized_text=[get_result(i) for i in range(0,len(ids),batch)]

        summarized_text=[i.strip() for i in summarized_text]

        summarized_result='. '.join(summarized_text)
        summarized_result = summarized_result.replace('..', '.')
        progress_bar.progress(90)
        st.subheader('Submitted Youtube Video:')
        st_player(youtube_video)
        progress_bar.progress(100)
        st.subheader('Summarized Result:')
        st.write(summarized_result)
        progress_bar.empty()
        state.text('\n Completed!')
    
      except:
        progress_bar.progress(100)
        progress_bar.empty()
        state.text('\n Completed!')
        st.write("The closed captions for this video are disabled! Please try with a video where the closed captions aren't disabled")

    else:
      st.text("Please enter a valid youtube link")


footer="""<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}
a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}
.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: white;
color: black;
text-align: center;
}
</style>
<div class="footer">
<p>Developed by <a style='display: block; text-align: center;' href="https://www.linkedin.com/in/pawan-kalyan-9704991aa/" target="_blank">Pawan Kalyan Jada</a></p>
<p>Email ID : <a style='display: block; text-align: center;' target="_blank">pawankalyanjada@gmail.com</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)