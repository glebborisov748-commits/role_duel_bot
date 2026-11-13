// Offline DOM integration test. Run with jsdom available in NODE_PATH.
const {JSDOM,ResourceLoader,VirtualConsole}=require('jsdom');
const fs=require('fs');const assert=require('assert');
const fixture=JSON.parse(fs.readFileSync(process.argv[2]||'/tmp/rd_ui_fixture.json','utf8'));
let state=fixture.state;const requests=[],errors=[];
class Loader extends ResourceLoader {
 fetch(url){
  if(url.endsWith('/tg-sdk.js'))return Promise.resolve(Buffer.from('window.Telegram={WebApp:{initData:"fixture",platform:"web",ready(){},expand(){},setHeaderColor(){},setBackgroundColor(){},disableVerticalSwipes(){},BackButton:{hide(){}},showConfirm(t,cb){cb(true)},HapticFeedback:{selectionChanged(){},notificationOccurred(){},impactOccurred(){}}}};'));
  if(url.endsWith('/sfx.js'))return Promise.resolve(Buffer.from(fixture.constants.SFX_JS));
  if(url.endsWith('/theme.css'))return Promise.resolve(Buffer.from(fixture.constants.APP_THEME_CSS));
  if(url.includes('/guide'))return Promise.resolve(Buffer.from('<h1>Справка</h1>'));
  return null;
 }
}
const pause=()=>new Promise(resolve=>setTimeout(resolve,40));
function start(){
 const vc=new VirtualConsole();vc.on('jsdomError',e=>{if(e.type!=='not-implemented')errors.push(e.message);});
 return new JSDOM(fixture.constants.APP_PAGE_HTML.replace('<head>','<head><script src="/sfx.js"></script>'),{
  url:'https://roleduel.test/app',pretendToBeVisual:true,runScripts:'dangerously',resources:new Loader(),virtualConsole:vc,
  beforeParse(w){w.confirm=()=>true;w.AbortController=AbortController;
   w.fetch=async(path,opts)=>{
    const body=opts.body?JSON.parse(opts.body):{};requests.push([path,body]);
    if(path==='/api/app/settings'){Object.assign(state.settings,body);if(body.lang)state.ui=fixture.constants.APP_TEXTS[body.lang];}
    if(path==='/api/app/message'){
     const m=state.messages.find(m=>m.id===body.id);assert(m);
     if(body.action==='edit')Object.assign(m,{text:body.text,edited:true});
     if(body.action==='delete')state.messages.splice(state.messages.indexOf(m),1);
     if(body.action==='react')m.user_reaction=m.user_reaction===body.emoji?null:body.emoji;
    }
    return {json:async()=>({ok:true,state:JSON.parse(JSON.stringify(state))})};
   };
  }
 });
}
function button(d,text){const b=[...d.querySelectorAll('button')].find(b=>b.textContent===text);assert(b,'Missing button '+text);return b;}
(async()=>{
 const dom=start(),w=dom.window,d=w.document;await pause();await pause();
 assert(d.querySelectorAll('#msgs .bub').length===2,'chat rendered');
 d.querySelector('#msgs .bub').dispatchEvent(new w.MouseEvent('contextmenu',{bubbles:true,cancelable:true}));
 button(d,'Редактировать').click();d.querySelector('#sheet-box textarea').value='Новый текст';button(d,'Сохранить').click();await pause();
 assert(d.querySelector('#msgs').textContent.includes('Новый текст'));assert(d.querySelector('.rd-edited'));
 d.querySelectorAll('#msgs .bub')[1].dispatchEvent(new w.MouseEvent('contextmenu',{bubbles:true,cancelable:true}));button(d,'❤️').click();await pause();
 assert.equal(d.querySelector('.rd-user-react').textContent,'❤️');
 d.querySelectorAll('#nav button')[5].click();await pause();
 assert(d.querySelector('#view-profile').textContent.includes('Пополнить баксы'));assert(d.querySelector('#view-profile ul').textContent.length>20);
 assert(d.querySelectorAll('#view-profile .rd-pack').length===3);
 button(d,fixture.constants.APP_TEXTS.ru.guide_btn).click();assert(d.querySelector('iframe.rd-guide'));
 button(d,'Показать, что где находится').click();assert(d.querySelector('.rd-tour'));button(d,'Пропустить').click();await pause();assert(!d.querySelector('.rd-tour'));
 d.querySelectorAll('#nav button')[5].click();await pause();
 const language=d.querySelector('select');language.value='en';language.dispatchEvent(new w.Event('change'));await pause();
 assert(d.querySelector('#view-profile').textContent.includes('Conversation mode'));
 const mode=d.querySelectorAll('select')[1];mode.value='live';mode.dispatchEvent(new w.Event('change'));await pause();assert.equal(state.settings.scene,'live');
 d.querySelectorAll('#nav button')[0].click();await pause();d.querySelector('#msgs .bub').dispatchEvent(new w.MouseEvent('contextmenu',{bubbles:true,cancelable:true}));button(d,'Delete').click();await pause();assert.equal(state.messages.length,1);
 assert.deepEqual(errors,[]);
 state.onboarding={lang:'ru',default_gender:'female',worlds:[{key:'realism',label:'Мир'}],genders:[{key:'female',label:'Девушка'}],styles:[{key:'warm',label:'Тёплый'}],scenes:[{key:'phone',label:'Переписка'},{key:'live',label:'Ролеплей'}],looks:[{key:'test',world:'realism',gender:'female',img:'/assets/avatar_real_f1.jpg',label:'Портрет'}],can_custom:false};
 state.ui=fixture.constants.APP_TEXTS.ru;
 const onboarding=start();await pause();await pause();const od=onboarding.window.document;
 button(od,'Мир').click();button(od,state.ui.ob_next).click();
 button(od,state.ui.ob_next).click();
 button(od,'Портрет').click();button(od,state.ui.ob_next).click();
 button(od,'Тёплый').click();button(od,state.ui.ob_next).click();
 button(od,'Ролеплей').click();button(od,state.ui.ob_done).click();await pause();
 assert(requests.some(([path,body])=>path==='/api/app/create'&&body.scene==='live'));
 assert.deepEqual(errors,[]);
 console.log('DOM integration passed: chat edit/delete/reaction, profile perks/packs, embedded guide, tour, language/mode, five-step creation');
 process.exit(0);
})().catch(e=>{console.error(e);process.exit(1);});
