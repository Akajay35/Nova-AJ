const form=document.querySelector("#chat-form");
const input=document.querySelector("#message");
const conversation=document.querySelector("#conversation");
const emptyState=document.querySelector("#empty-state");
const sendButton=document.querySelector("#send-button");
const voiceButton=document.querySelector("#voice-button");
const installButton=document.querySelector("#install-button");
const connection=document.querySelector("#connection");
const modelLabel=document.querySelector("#model-label");
const notice=document.querySelector("#notice");
let installPrompt=null;

function addMessage(role,text){
  emptyState.hidden=true;
  const article=document.createElement("article");
  article.className="message "+role;
  const label=document.createElement("div");
  label.className="message-label";
  label.textContent=role==="user"?"You":"Nova AJ";
  const body=document.createElement("div");
  body.textContent=text;
  article.append(label,body);
  conversation.append(article);
  article.scrollIntoView({behavior:"smooth",block:"nearest"});
  return body;
}
async function checkStatus(){
  try{
    const response=await fetch("/api/status",{headers:{Accept:"application/json"}});
    if(!response.ok)throw new Error("API status unavailable");
    const status=await response.json();
    connection.textContent="API connected";
    connection.className="status online";
    modelLabel.textContent=status.ai_configured==="true"?"Model: "+status.model:"AI key not configured";
  }catch{
    connection.textContent="API unavailable";
    connection.className="status offline";
    modelLabel.textContent="Check the backend service";
  }
}
async function sendMessage(text){
  const message=text.trim();
  if(!message)return;
  notice.textContent="";
  addMessage("user",message);
  input.value="";
  sendButton.disabled=true;
  voiceButton.disabled=true;
  const replyBox=addMessage("assistant","Thinking…");
  try{
    const response=await fetch("/api/chat",{
      method:"POST",
      headers:{"Content-Type":"application/json","Accept":"application/json"},
      body:JSON.stringify({message})
    });
    const data=await response.json().catch(()=>({}));
    if(!response.ok){
      const detail=typeof data.detail==="string"?data.detail:"Request failed ("+response.status+")";
      replyBox.textContent=detail;
      notice.textContent=response.status===503?"Configure OPENAI_API_KEY in the server environment to enable AI replies.":"";
    }else{
      replyBox.textContent=data.reply||"The assistant returned an empty response.";
      if(data.model)modelLabel.textContent="Model: "+data.model;
    }
  }catch{
    replyBox.textContent="I couldn't reach the Nova AJ API. Check your connection and try again.";
    notice.textContent="The chat request failed. Your message has not been confirmed as processed.";
  }finally{
    sendButton.disabled=false;
    voiceButton.disabled=false;
    input.focus();
  }
}
form.addEventListener("submit",event=>{event.preventDefault();sendMessage(input.value)});
document.querySelectorAll("[data-prompt]").forEach(button=>button.addEventListener("click",()=>{input.value=button.dataset.prompt;input.focus()}));
input.addEventListener("keydown",event=>{
  if(event.key==="Enter"&&!event.shiftKey&&!event.isComposing){event.preventDefault();form.requestSubmit()}
});
const SpeechRecognition=window.SpeechRecognition||window.webkitSpeechRecognition;
if(SpeechRecognition){
  voiceButton.addEventListener("click",()=>{
    const recognition=new SpeechRecognition();
    recognition.lang="en-IN";
    recognition.interimResults=false;
    recognition.maxAlternatives=1;
    voiceButton.disabled=true;
    notice.textContent="Listening…";
    recognition.onresult=event=>{input.value=event.results[0][0].transcript;notice.textContent="Voice captured. Review it, then press Send.";input.focus()};
    recognition.onerror=()=>{notice.textContent="Voice input wasn't available. You can type your message instead."};
    recognition.onend=()=>{voiceButton.disabled=false;if(notice.textContent==="Listening…")notice.textContent=""};
    try{recognition.start()}catch{voiceButton.disabled=false;notice.textContent="Could not start voice input."}
  });
}else{
  voiceButton.disabled=true;
  voiceButton.title="Voice input is not supported by this browser";
}
window.addEventListener("beforeinstallprompt",event=>{
  event.preventDefault();
  installPrompt=event;
  installButton.hidden=false;
});
installButton.addEventListener("click",async()=>{
  if(!installPrompt)return;
  installPrompt.prompt();
  await installPrompt.userChoice;
  installPrompt=null;
  installButton.hidden=true;
});
if("serviceWorker" in navigator){
  window.addEventListener("load",()=>navigator.serviceWorker.register("/app/service-worker.js",{scope:"/app/"}).catch(()=>{}));
}
checkStatus();
