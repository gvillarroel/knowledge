/** Send one stateless, explicitly selected request through a copied local runtime. */
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const config=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const request=JSON.parse(fs.readFileSync(0,'utf8'));
const provider=request.provider;
if(!['github-copilot','openai-codex'].includes(provider)){
  throw new Error('The requested provider is outside the explicit evaluation allowlist');
}
if(!['gpt-5.4','gpt-5.6-luna'].includes(request.model)){
  throw new Error('The requested model is outside the explicit evaluation allowlist');
}
const {ModelRuntime}=await import(pathToFileURL(path.join(config.piPackageRoot,'dist/core/model-runtime.js')).href);
const runtime=await ModelRuntime.create({authPath:config.authPath,modelsPath:null,
  modelsStorePath:config.modelsStorePath,allowModelNetwork:false,refreshOnCreate:false});
const model=runtime.getModel(provider,request.model);
const expectedApi=provider==='openai-codex'?'openai-codex-responses':'openai-responses';
if(!model || model.api!==expectedApi)throw new Error('Declared subscription model is unavailable');
if(request.messages.some(m=>m.role!=='user' || typeof m.content!=='string')){
  throw new Error('Only stateless upstream user messages are permitted');
}
let providerPayload;
const responses=[];
const originalFetch=globalThis.fetch;
const response=await runtime.completeSimple(model,{messages:request.messages.map(m=>({...m,timestamp:0}))},
  {reasoning:'medium',maxTokens:request.max_output_tokens,maxRetries:0,
   signal:AbortSignal.timeout(600000),transport:'sse',
   onPayload(payload){
     if(payload.model!==request.model || payload.reasoning?.effort!=='medium'
         || payload.tools?.length || payload.store!==false){
       throw new Error('Declared inference parameters changed');
     }
     if(provider==='github-copilot' && payload.max_output_tokens!==request.max_output_tokens){
       throw new Error('Declared output cap changed');
     }
     // Codex uses its subscription protocol, which has no max_output_tokens
     // field. Record the default system instruction and explicit verbosity;
     // the host rejects responses over its declared acceptance limit.
     if(provider==='openai-codex' && (payload.max_output_tokens!==undefined
         || payload.instructions!=='You are a helpful assistant.' || payload.text?.verbosity!=='low')){
       throw new Error('Declared Codex protocol changed');
     }
     providerPayload=payload;
   },
   async fetch(input,init){
     const result=await originalFetch(input,init);
     responses.push({status:result.status,body:result.clone().text()});
     return result;
   }});
const completed=[];
const completedItems=[];
let httpStatus;
for(const item of responses){
  httpStatus=item.status;
  for(const line of (await item.body).split(/\r?\n/)){
    if(!line.startsWith('data: ') || line==='data: [DONE]')continue;
    let event;
    try{event=JSON.parse(line.slice(6));}catch{continue;}
    if(event.type==='response.completed' || event.type==='response.incomplete')completed.push(event.response);
    if(event.type==='response.output_item.done')completedItems.push(event.item);
  }
}
const result=completed.at(-1);
// The provider event, rather than the SDK's configured model label, binds the
// returned model and exact usage. Authentication headers are never serialized.
if(responses.length!==1 || !result || response.stopReason!=='stop'){
  console.log(JSON.stringify({status:'unavailable',http_status:httpStatus,
    request_count:responses.length,stop_reason:response.stopReason,
    error_categories:['unsupported','expired','quota','rate limit','401','403','429','usage','context','limit'].filter(
      s=>(response.errorMessage??'').toLowerCase().includes(s))}));
  process.exit(3);
}
// Codex can leave response.completed.output empty while sending the final
// message in response.output_item.done. Reconstruct only completed messages,
// then require exact agreement with the SDK's decoded text from that stream.
const fromItems=!result.output?.length;
const output=fromItems?completedItems.filter(item=>item?.type==='message'):result.output;
const decodedText=output.filter(item=>item.type==='message').flatMap(item=>item.content??[])
  .filter(part=>part.type==='output_text').map(part=>part.text).join('');
const sdkText=response.content.filter(part=>part.type==='text').map(part=>part.text).join('');
if(decodedText!==sdkText){
  if(process.argv[3])fs.writeFileSync(process.argv[3]+'.diagnostic.json',
    JSON.stringify({provider_response:result,completed_items:completedItems,sdk_text:sdkText,
      decoded_text:decodedText,provider_payload:providerPayload}),{flag:'wx'});
  throw new Error('Completed stream text does not match the SDK response');
}
const finalResult={...result,bridge:{provider,request_count:responses.length,
  http_status:httpStatus,provider_payload:providerPayload,pi_usage_estimate:response.usage,
  output_reconstructed_from_completed_items:fromItems,sdk_stream_text_match:true,
  empty_completed_text:decodedText.length===0},output};
// Persist a completed reply before process shutdown or stdout delivery. The
// host supplies a fresh path inside its private call directory.
if(process.argv[3]){
  const temporary=process.argv[3]+'.tmp';
  fs.writeFileSync(temporary,JSON.stringify(finalResult),{flag:'wx'});
  fs.renameSync(temporary,process.argv[3]);
}
console.log(JSON.stringify(finalResult));
process.exit(0);
