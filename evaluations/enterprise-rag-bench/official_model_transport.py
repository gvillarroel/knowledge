"""Explicit model transport for public-protocol and internal answer evaluations."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import math
import os
import re
from pathlib import Path
import subprocess
import threading
import time
import urllib.error
import urllib.request


class TransportUnavailable(RuntimeError):
    """The declared model could not produce an evaluable response."""


def bound_subscription_completion(result: dict, provider: str, model: str, messages: list[dict]) -> bool:
    """Recognize a final bridge receipt even if the child fails during shutdown."""
    bridge=result.get('bridge') or {}
    payload=bridge.get('provider_payload') or {}
    expected=[{'role':m['role'],'content':[{'type':'input_text','text':m['content']}]} for m in messages]
    return (result.get('status')=='completed' and bridge.get('http_status')==200
            and bridge.get('request_count')==1 and bridge.get('provider')==provider
            and payload.get('model')==model and payload.get('input')==expected
            and (payload.get('reasoning') or {}).get('effort')=='medium'
            and (result.get('reasoning') or {}).get('effort')=='medium'
            and payload.get('store') is False and not payload.get('tools')
            and (bool(result.get('output')) or
                 bridge.get('sdk_stream_text_match') is True and bridge.get('empty_completed_text') is True))


class ModelTransport:
    """Keep credentials out of artifacts and preserve every actual call.

    Provider choice is explicit and immutable. There is no model or provider
    fallback and no HTTP retry. Upstream JSON parsing retries remain upstream.
    """

    def __init__(self, provider: str, output: Path, budget_usd: float = 50.0, concurrency: int = 8,
                 model: str = 'gpt-5.4', allow_empty: bool = False):
        if provider not in {'openai', 'openrouter', 'github-copilot', 'openai-codex'}:
            raise ValueError('Unsupported explicit provider')
        if model not in {'gpt-5.4','gpt-5.6-luna'}:
            raise ValueError('Unsupported explicit model')
        if not math.isfinite(budget_usd) or budget_usd <= 0:
            raise ValueError('A positive finite budget is required')
        self.provider, self.output, self.budget, self.model = provider, output, budget_usd, model
        self.allow_empty = allow_empty
        self.key = os.environ.get('ENTERPRISE_CODEX_CONFIG' if provider=='openai-codex'
                                  else 'ENTERPRISE_COPILOT_CONFIG' if provider=='github-copilot'
                                  else 'LLM_API_KEY' if provider == 'openai' else 'OPENROUTER_API_KEY')
        if not self.key:
            raise TransportUnavailable('Required provider credential is unavailable')
        output.mkdir(parents=True, exist_ok=False)
        self.condition = threading.Condition()
        self.slots = threading.Semaphore(concurrency)
        self.local = threading.local()
        self.next_call = 0
        self.spent = self.reserved = 0.0
        self.errors = 0
        self.halted = False
        self.usage = {'input_tokens':0, 'output_tokens':0, 'cached_input_tokens':0}

    @contextmanager
    def scope(self, label: str):
        """Bind host request provenance without exposing it to the model."""
        previous = getattr(self.local, 'label', None)
        self.local.label = label
        try:
            yield
        finally:
            self.local.label = previous

    def complete(self, messages: list[dict], max_tokens: int = 8192) -> str:
        """Send one stateless prompt and require an untruncated declared-model reply."""
        if any(m.get('role') not in {'system','user','assistant'} or not isinstance(m.get('content'),str)
               for m in messages):
            raise ValueError('Only text messages are allowed')
        # UTF-8 byte count is a conservative input-token bound. Reserve at the
        # long-context rate; settle against actual provider usage afterwards.
        rates=self.token_rates(long_context=True)
        # The Codex subscription endpoint does not accept an output-token cap.
        # Reserve its full declared model maximum, then enforce the host limit.
        reserve_output=128000 if self.provider=='openai-codex' else max_tokens
        reserve = ((sum(len(m['content'].encode('utf-8')) for m in messages)+2048)*rates[0]
                   + reserve_output*rates[2])/1e6
        with self.slots:
            with self.condition:
                while self.spent+self.reserved+reserve > self.budget and self.reserved > 0 and not self.halted:
                    self.condition.wait(timeout=5)
                if self.halted or self.spent+self.reserved+reserve > self.budget:
                    raise TransportUnavailable('Model execution stopped at its declared availability or cost boundary')
                number = self.next_call
                self.next_call += 1
                self.reserved += reserve
            if self.provider == 'openrouter':
                endpoint = 'https://openrouter.ai/api/v1/chat/completions'
                payload = {'model':'openai/'+self.model, 'messages':messages,
                           'reasoning':{'effort':'medium'}, 'max_tokens':max_tokens,
                           'provider':{'order':['OpenAI'],'allow_fallbacks':False,'require_parameters':True}}
            elif self.provider=='openai':
                endpoint = 'https://api.openai.com/v1/responses'
                payload = {'model':self.model, 'input':messages, 'reasoning':{'effort':'medium'},
                           'max_output_tokens':max_tokens, 'store':False}
            else:
                payload={'provider':self.provider,'model':self.model,'messages':messages,'reasoning':{'effort':'medium'},
                         'max_output_tokens':max_tokens}
            request_bytes = json.dumps(payload,ensure_ascii=False,allow_nan=False).encode('utf-8')
            started = time.perf_counter()
            receipt = {'call':number, 'scope':getattr(self.local,'label',None),
                       'provider':self.provider,'model':self.model,'reasoning':'medium',
                       'request_sha256':hashlib.sha256(request_bytes).hexdigest(),
                       'request':payload,'status':'unavailable'}
            cost = 0.0
            input_tokens = output_tokens = cached = 0
            try:
                if self.provider in {'github-copilot','openai-codex'}:
                    node=json.loads(Path(self.key).read_text(encoding='utf-8'))['node_executable']
                    bridge=Path(__file__).resolve().with_name('subscription_model_bridge.mjs')
                    durable=self.output/'provider-responses'/f'{number:06d}.json'
                    durable.parent.mkdir(exist_ok=True)
                    child=subprocess.run([node,str(bridge),self.key,str(durable)],input=request_bytes,
                                         stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=630)
                    receipt['bridge_exit_code']=child.returncode
                    logs=self.output/'bridge-logs'
                    logs.mkdir(exist_ok=True)
                    for label,data in [('stdout',child.stdout),('stderr',child.stderr)]:
                        with (logs/f'{number:06d}.{label}').open('xb') as stream:
                            stream.write(data)
                        receipt['bridge_'+label+'_sha256']=hashlib.sha256(data).hexdigest()
                    if durable.exists():
                        result=json.loads(durable.read_text(encoding='utf-8'))
                        if not bound_subscription_completion(result,self.provider,self.model,messages):
                            raise TransportUnavailable('Durable bridge reply does not match the declared request')
                        receipt['durable_provider_reply']=durable.relative_to(self.output).as_posix()
                    else:
                        result=json.loads(child.stdout)
                    recovered_exit=child.returncode and bound_subscription_completion(
                        result,self.provider,self.model,messages)
                    if (child.returncode and not recovered_exit) or result.get('status')!='completed':
                        receipt['bridge_failure']=result
                        raise TransportUnavailable('Subscription request was unavailable')
                    if recovered_exit:
                        receipt['completed_reply_preserved_after_child_exit_error']=True
                else:
                    request = urllib.request.Request(endpoint,data=request_bytes,headers={
                        'Authorization':'Bearer '+self.key,'Content-Type':'application/json'})
                    with urllib.request.urlopen(request,timeout=600) as response:
                        result = json.load(response)
                usage = result.get('usage') or {}
                receipt['response'] = result
                actual_model = result.get('model','')
                if not re.fullmatch(r'(?:openai/)?'+re.escape(self.model)+r'(?:-\d{4}-\d{2}-\d{2})?',actual_model):
                    raise TransportUnavailable('Provider returned a different model')
                if self.provider == 'openrouter':
                    input_tokens, output_tokens = usage['prompt_tokens'], usage['completion_tokens']
                    cached = (usage.get('prompt_tokens_details') or {}).get('cached_tokens',0)
                    cost = float(usage['cost'])
                    choice = result['choices'][0]
                    text = choice['message'].get('content') or ''
                    complete = choice.get('finish_reason') == 'stop'
                else:
                    input_tokens, output_tokens = usage['input_tokens'], usage['output_tokens']
                    cached = (usage.get('input_tokens_details') or {}).get('cached_tokens',0)
                    threshold=200000 if self.model=='gpt-5.6-luna' and self.provider=='github-copilot' else 272000
                    rates=self.token_rates(long_context=input_tokens>threshold)
                    cost=((input_tokens-cached)*rates[0]+cached*rates[1]+output_tokens*rates[2])/1e6
                    text = ''.join(part.get('text','') for item in result.get('output',[])
                                   if item.get('type')=='message' for part in item.get('content',[])
                                   if part.get('type')=='output_text')
                    complete = result.get('status') == 'completed'
                if not math.isfinite(cost) or cost < 0:
                    raise TransportUnavailable('Provider did not report valid usage')
                if not complete or (not text.strip() and not self.allow_empty):
                    raise TransportUnavailable('Missing or truncated model response')
                if self.provider=='openai-codex' and output_tokens>max_tokens:
                    raise TransportUnavailable('Codex response exceeded the declared host output limit')
                receipt['status']='complete'
                return text.strip()
            except Exception as error:
                receipt['error_type']=type(error).__name__
                if isinstance(error,urllib.error.HTTPError):
                    receipt['http_status']=error.code
                with self.condition:
                    self.errors += 1
                    self.halted = True
                raise TransportUnavailable('Declared model request was unavailable; inspect the private call receipt') from None
            finally:
                receipt.update(seconds=time.perf_counter()-started,cost_usd=cost,
                    cost_basis=self.cost_basis())
                with (self.output/f'{number:06d}.json').open('x',encoding='utf-8') as stream:
                    json.dump(receipt,stream,ensure_ascii=False,allow_nan=False)
                with self.condition:
                    self.spent += cost
                    self.reserved -= reserve
                    self.usage['input_tokens'] += input_tokens
                    self.usage['output_tokens'] += output_tokens
                    self.usage['cached_input_tokens'] += cached
                    self.condition.notify_all()

    def get_llm(self, tools=None, quiet=False, reasoning_level='medium', model=None):
        """Implement the upstream factory interface without changing its prompts."""
        if tools or reasoning_level!='medium' or model not in {None,self.model}:
            raise ValueError('The evaluation permits only the declared text-only model and medium reasoning')
        transport=self

        class LLM:
            def generate(self, messages):
                """Yield the full text through the unchanged upstream interface."""
                yield transport.complete([{'role':m.role,'content':m.content} for m in messages])

        return LLM()

    def summary(self) -> dict:
        """Return aggregate resource and availability data without credentials."""
        return {'provider':self.provider,'model':self.model,'reasoning':'medium',
                'calls':self.next_call,'transport_errors':self.errors,'cost_usd':self.spent,
                'cost_basis':self.cost_basis(),
                'budget_usd':self.budget, **self.usage}

    def cost_basis(self) -> str:
        """Distinguish provider bills from token-rate estimates on subscriptions."""
        if self.provider=='openrouter':
            return 'provider-reported'
        if self.provider=='github-copilot':
            return 'OpenAI-token-rate-equivalent; not a Copilot invoice'
        if self.provider=='openai-codex':
            return 'frozen-runtime-token-rate-equivalent; not a Codex invoice'
        return 'published-token-rate-estimate'

    def token_rates(self, long_context: bool = False) -> tuple[float,float,float]:
        """Return frozen input, cached-input and output rates per million tokens."""
        if self.model=='gpt-5.6-luna':
            return (0.4,0.04,1.8) if long_context else (0.2,0.02,1.2)
        return (5.0,0.5,22.5) if long_context else (2.5,0.25,15.0)
