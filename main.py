import os, re, json, uuid, time, argparse
import traceback
from typing import List
from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langfuse.langchain import CallbackHandler

class CodeReviewOutput(BaseModel):
    identified_issues: List[str]
    improvement_suggestions: List[str]
    code_quality_level: str
    review_summary: str


def parse_review_output(raw: str) -> CodeReviewOutput:
    clean = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    clean = re.sub(r"\s*```$", "", clean).strip()
    return CodeReviewOutput(**json.loads(clean))


def get_prompt_template():
    return ChatPromptTemplate.from_messages([
        ("system", """You are a senior software engineer doing code review.
Respond ONLY with this JSON, no extra text:
{{
  "identified_issues": ["issues here"],
  "improvement_suggestions": ["suggestions here"],
  "code_quality_level": "Excellent or Good or Moderate or Low or Critical",
  "review_summary": "short summary here"
}}"""),
       ("human", "Review this code:\n\n```\n{code_snippet}\n```"),
    ])


def get_llm():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise EnvironmentError("GROQ_API_KEY not set in .env")
    return ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2,
    api_key=key
)


def get_langfuse_handler(session_id, trace_name):
    return CallbackHandler()


def review_code(code_snippet, session_id=None, trace_name="code-review"):
    session_id = session_id or f"session-{uuid.uuid4().hex[:8]}"
    chain = get_prompt_template() | get_llm()

    response = chain.invoke(
        {"code_snippet": code_snippet}
    )

    return parse_review_output(response.content)


TEST_SNIPPETS = [
    "def factorial(n):\n    if n < 0: raise ValueError('negative')\n    return 1 if n == 0 else n * factorial(n-1)",
    "def binary_search(arr, target):\n    lo, hi = 0, len(arr)-1\n    while lo <= hi:\n        mid = (lo+hi)//2\n        if arr[mid]==target: return mid\n        elif arr[mid]<target: lo=mid+1\n        else: hi=mid-1\n    return -1",
    "class Stack:\n    def __init__(self): self._data=[]\n    def push(self,item): self._data.append(item)\n    def pop(self):\n        if not self._data: raise IndexError('empty')\n        return self._data.pop()",
    "import hashlib\ndef hash_password(p,s): return hashlib.sha256((p+s).encode()).hexdigest()",
    "def merge_sorted(a,b):\n    r,i,j=[],0,0\n    while i<len(a) and j<len(b):\n        if a[i]<=b[j]: r.append(a[i]);i+=1\n        else: r.append(b[j]);j+=1\n    return r+a[i:]+b[j:]",
    "def generate_token(n=32):\n    import secrets\n    return secrets.token_hex(n)",
    "def chunk_list(lst,size): return [lst[i:i+size] for i in range(0,len(lst),size)]",
    "def rotate_list(lst,k): k=k%len(lst); return lst[k:]+lst[:k]",
    "def validate_email(e):\n    import re\n    return bool(re.match(r'^[\\w.-]+@[\\w.-]+\\.\\w+$',e))",
    "def memoize(func):\n    cache={}\n    def wrapper(*args):\n        if args not in cache: cache[args]=func(*args)\n        return cache[args]\n    return wrapper",
    "def get_evens(numbers): return [n for n in numbers if n%2==0]",
    "def celsius_to_f(c): return (c*9/5)+32",
    "def count_words(s): return len(s.split())",
    "def is_palindrome(s): s=s.lower().replace(' ',''); return s==s[::-1]",
    "def flatten(nested):\n    r=[]\n    for item in nested:\n        if isinstance(item,list): r.extend(flatten(item))\n        else: r.append(item)\n    return r",
    "def find_max(lst): return max(lst) if lst else None",
    "def safe_divide(a,b): return None if b==0 else a/b",
    "def capitalize_words(s): return ' '.join(w.capitalize() for w in s.split())",
    "def sum_digits(n): return sum(int(d) for d in str(abs(n)))",
    "def word_freq(text):\n    from collections import Counter\n    return dict(Counter(text.lower().split()).most_common(10))",
    "def fibonacci(n):\n    a,b,seq=0,1,[]\n    while len(seq)<n: seq.append(a);a,b=b,a+b\n    return seq",
    "def retry(func,times=3):\n    for i in range(times):\n        try: return func()\n        except Exception as e:\n            if i==times-1: raise",
    "def group_by(items,key_fn):\n    g={}\n    for item in items: g.setdefault(key_fn(item),[]).append(item)\n    return g",
    "def remove_duplicates(items):\n    seen=set()\n    return [x for x in items if not(x in seen or seen.add(x))]",
    "def diff_dicts(old,new):\n    return {'added':{k:new[k] for k in new if k not in old},'removed':{k:old[k] for k in old if k not in new}}",
    "def calc(x,y,op):\n    if op=='add': return x+y\n    if op=='sub': return x-y\n    if op=='mul': return x*y\n    if op=='div': return x/y",
    "def process(data):\n    result=[]\n    for i in range(len(data)):\n        if data[i]!=None: result.append(data[i])\n    return result",
    "global_list=[]\ndef add_item(item):\n    global global_list\n    global_list.append(item)\n    return global_list",
    "def check_age(age):\n    if age>=18:\n        if age>=65: return 'senior'\n        else: return 'adult'\n    else:\n        if age>=13: return 'teen'\n        else: return 'child'",
    "def read_file(path):\n    f=open(path,'r')\n    c=f.read()\n    f.close()\n    return c",
    "numbers=[1,2,3,4,5]\ntotal=0\nfor i in range(len(numbers)): total+=numbers[i]\nprint(total/len(numbers))",
    "def get_user(id):\n    users={'1':'Alice','2':'Bob'}\n    for k in users:\n        if k==str(id): return users[k]\n    return 'Not found'",
    "def temp_convert(t,unit):\n    if unit=='C': return t*9/5+32\n    if unit=='F': return (t-32)*5/9\n    if unit=='K': return t-273.15",
    "import datetime\ndef get_age(year): return datetime.datetime.now().year-year",
    "def matrix_add(A,B): return [[A[i][j]+B[i][j] for j in range(len(A[0]))] for i in range(len(A))]",
    "import json\ndef load_config(path):\n    with open(path) as f: return json.load(f)",
    "def batch(items,size,func):\n    r=[]\n    for i in range(0,len(items),size): r.extend(func(items[i:i+size]))\n    return r",
    "def pipeline(data,*steps):\n    for s in steps: data=s(data)\n    return data",
    "def parse_csv(f):\n    with open(f) as fp: lines=fp.readlines()\n    h=lines[0].strip().split(',')\n    return [dict(zip(h,l.strip().split(','))) for l in lines[1:]]",
    "def priority_demo():\n    import heapq\n    h=[]\n    heapq.heappush(h,(2,'B'));heapq.heappush(h,(1,'A'));heapq.heappush(h,(3,'C'))\n    return [heapq.heappop(h) for _ in range(len(h))]",
    "def f(l):\n    s=0\n    for i in l: s=s+i\n    return s/len(l)",
    "def d(a,b): return a/b",
    "x=input('num: ')\nprint(x*2)",
    "def check(s):\n    for i in range(len(s)):\n        for j in range(len(s)):\n            if s[i]==s[j] and i!=j: return True\n    return False",
    "pw='admin123'\ndb='mysql://user:admin123@localhost/prod'\nprint('connecting to',db)",
    "def sq(n): return n*n\ndef cb(n): return n*n*n\ndef pw(n,e): return n**e",
    "data=[3,1,4,1,5]\nfor i in range(len(data)):\n    for j in range(len(data)):\n        if data[i]<data[j]: tmp=data[i];data[i]=data[j];data[j]=tmp",
    "def login(u,p):\n    if u=='admin' and p=='password': return True\n    return False",
    "class c:\n    def __init__(s,n,a): s.n=n;s.a=a\n    def p(s): print(s.n,s.a)",
    "def get_data(q):\n    import sqlite3\n    conn=sqlite3.connect('db.sqlite')\n    cur=conn.cursor()\n    cur.execute(\"SELECT * FROM users WHERE name='\"+q+\"'\")\n    return cur.fetchall()",
    "def divide(a,b):\n    try: return a/b\n    except: pass",
    "def append_to(e,to=[]): to.append(e); return to",
    "def build(words):\n    r=''\n    for w in words: r=r+w+' '\n    return r.strip()",
    "def get_score(scores,name): return scores[name]",
    "counter=0\ndef increment():\n    global counter\n    for _ in range(1000): counter+=1",
    "def list(items): return [str(i) for i in items]",
    "def calculate(x,y):\n    print('DEBUG x=',x)\n    r=x**y\n    print('DEBUG r=',r)\n    return r",
    "def discount(price):\n    if price>1000: return price*0.85\n    elif price>500: return price*0.90\n    return price*0.95",
    "def transfer(amount):\n    assert amount>0,'must be positive'\n    return amount*1.02",
    "for i in range(5):\nprint(i)",
    "def greet(name)\n    print('Hello '+name)",
    "x=10\ny=0\nz=x/y\nprint(z)",
    "import subprocess\ncmd=input('command: ')\nsubprocess.call(cmd,shell=True)",
    "lst=[1,2,3]\nprint(lst[5])",
    "def infinite():\n    while True: pass\ninfinite()",
    "eval(input('expression: '))",
    "def add(a,b): return a+b\nresult=add(1,2,3)\nprint(result)",
    "class Dog\n    def __init__(self,name): self.name=name",
    "import pickle\ndef load(data): return pickle.loads(data)",
    "import requests\ndef weather(city): return requests.get(f'https://api.weather.com/{city}').json()",
    "from functools import reduce\ndef product(nums): return reduce(lambda x,y:x*y,nums,1)",
    "class Counter:\n    count=0\n    def inc(self): Counter.count+=1\n    def get(self): return Counter.count",
    "def levenshtein(s1,s2):\n    m,n=len(s1),len(s2)\n    dp=[[0]*(n+1) for _ in range(m+1)]\n    for i in range(m+1): dp[i][0]=i\n    for j in range(n+1): dp[0][j]=j\n    for i in range(1,m+1):\n        for j in range(1,n+1):\n            cost=0 if s1[i-1]==s2[j-1] else 1\n            dp[i][j]=min(dp[i-1][j]+1,dp[i][j-1]+1,dp[i-1][j-1]+cost)\n    return dp[m][n]",
    "def zip_files(paths,out):\n    import zipfile\n    with zipfile.ZipFile(out,'w') as zf:\n        for f in paths: zf.write(f)",
    "def trie_insert(trie,word):\n    node=trie\n    for ch in word: node=node.setdefault(ch,{})\n    node['#']=True",
    "class Singleton:\n    _i=None\n    def __new__(cls):\n        if not cls._i: cls._i=super().__new__(cls)\n        return cls._i",
    "def detect_cycle(graph,start):\n    visited,stack=set(),set()\n    def dfs(node):\n        visited.add(node);stack.add(node)\n        for nb in graph.get(node,[]):\n            if nb not in visited:\n                if dfs(nb): return True\n            elif nb in stack: return True\n        stack.remove(node);return False\n    return dfs(start)",
    "async def fetch_all(urls):\n    import aiohttp\n    async with aiohttp.ClientSession() as s:\n        r=[]\n        for url in urls:\n            async with s.get(url) as resp: r.append(await resp.json())\n    return r",
    "class Point:\n    def __init__(self,x,y): self.x=x;self.y=y",
    "def has_positive(nums):\n    found=False\n    for n in nums:\n        if n>0: found=True;break\n    return found",
    "def safe_run(func):\n    try: return func()\n    except BaseException: return None",
    "from math import *\ndef area(r): return pi*r**2",
    "def write_log(msg):\n    f=open('log.txt','a')\n    f.write(msg+'\\n')",
    "def parse_value(s):\n    try: return int(s)\n    except: return s",
    "def classify(n):\n    if n>0:\n        if n<10:\n            if n%2==0: return 'small even'\n            else: return 'small odd'\n        else:\n            if n%2==0: return 'large even'\n            else: return 'large odd'\n    else: return 'non-positive'",
    "def create_user(d): return {'name':d['name'],'email':d['email'],'age':d['age']}",
    "def bmi(w,h):\n    b=w/(h**2)\n    if b<18.5: return 1\n    elif b<25: return 2\n    elif b<30: return 3\n    else: return 4",
    "def poll(api,tries=10):\n    for _ in range(tries):\n        if api()=='done': return True\n        time.sleep(5)\n    return False",
    "def throttle(n):\n    import time\n    interval=1.0/n\n    last=[0.0]\n    def dec(func):\n        def wrap(*args):\n            e=time.time()-last[0]\n            if e<interval: time.sleep(interval-e)\n            r=func(*args);last[0]=time.time();return r\n        return wrap\n    return dec",
    "def lru(cap):\n    from collections import OrderedDict\n    c=OrderedDict()\n    def get(k):\n        if k not in c: return -1\n        c.move_to_end(k);return c[k]\n    def put(k,v):\n        if k in c: c.move_to_end(k)\n        c[k]=v\n        if len(c)>cap: c.popitem(last=False)\n    return get,put",
    "def run(data,*steps):\n    for s in steps: data=s(data)\n    return data",
    "def serialize(obj):\n    import pickle\n    return pickle.dumps(obj)\ndef deserialize(data):\n    import pickle\n    return pickle.loads(data)",
      "def add_matrix(A,B):\n    return [[A[i][j]+B[i][j] for j in range(len(A[0]))] for i in range(len(A))]",
    "def count_vowels(s):\n    return sum(1 for c in s.lower() if c in 'aeiou')",
    "def reverse_string(s):\n    return s[::-1]",
    "def is_even(n):\n    return n%2==0",
    "def power(base,exp):\n    return base**exp",
    "def absolute(n):\n    return n if n>=0 else -n",
    "def greet(name):\n    return f'Hello, {name}!'",
    "def square_list(nums):\n    return [n**2 for n in nums]",
]

assert len(TEST_SNIPPETS) == 100, f"Need 100 snippets, got {len(TEST_SNIPPETS)}"


def run_100_traces(delay=0.3):
    session_id = f"batch-{uuid.uuid4().hex[:8]}"
    passed = failed = 0
    print(f"\n{'='*60}")
    print(f"  Running 100 traces to Langfuse | provider: Groq")
    print(f"  Session: {session_id}")
    print(f"{'='*60}\n")
    for idx, snippet in enumerate(TEST_SNIPPETS, 1):
        preview = snippet.replace("\n", " ")[:50]
        try:
            result = review_code(
                code_snippet=snippet,
                session_id=session_id,
                trace_name=f"trace-{idx:03d}",
            )
            passed += 1
            print(f"  [{idx:3d}/100] ✅  {result.code_quality_level:<10}  {preview}…")
        except Exception as e:
            failed += 1
            print(f"  [{idx:3d}/100] ❌  {e}")
        if delay > 0:
            time.sleep(delay)
    print(f"\n  ✅ Passed: {passed}  ❌ Failed: {failed}")
    print(f"  View at: https://cloud.langfuse.com  Session: {session_id}\n")


def run_streamlit_ui():
    import streamlit as st

    st.set_page_config(page_title="Code Review Feedback Generator", page_icon="🔍", layout="wide")

    st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .hero { background: linear-gradient(135deg,#161b22,#21262d);
        border-left: 4px solid #58a6ff; border-radius: 10px;
        padding: 22px 28px; margin-bottom: 24px; }
    .hero h1 { color: #e6edf3; font-size: 1.7rem; margin: 0 0 6px; }
    .hero p  { color: #8b949e; margin: 0; font-size: 0.9rem; }
    .card { background: #161b22; border: 1px solid #30363d;
        border-radius: 8px; padding: 18px 22px; margin-bottom: 14px; }
    .card-title { font-size: 0.7rem; font-weight: 700; letter-spacing: 1px;
        text-transform: uppercase; color: #58a6ff; margin: 0 0 10px; }
    .badge { display:inline-block; padding:5px 16px; border-radius:20px; font-weight:700; font-size:0.95rem; }
    .q-Excellent { background:#0d2b1e; color:#56d364; border:1px solid #56d364; }
    .q-Good      { background:#162a1e; color:#3fb950; border:1px solid #3fb950; }
    .q-Moderate  { background:#2d2000; color:#d29922; border:1px solid #d29922; }
    .q-Low       { background:#2d1200; color:#f0883e; border:1px solid #f0883e; }
    .q-Critical  { background:#2d0f0f; color:#f85149; border:1px solid #f85149; }
    .issue { background:#1e0d0d; border-left:3px solid #f85149; border-radius:4px;
        padding:7px 14px; margin-bottom:7px; color:#f0b8b8; font-size:0.9rem; }
    .sug   { background:#0d1e12; border-left:3px solid #56d364; border-radius:4px;
        padding:7px 14px; margin-bottom:7px; color:#a8f0b0; font-size:0.9rem; }
    .summary { background:#161b22; border:1px solid #58a6ff44; border-radius:6px;
        padding:14px 18px; color:#cdd9e5; font-size:0.95rem; line-height:1.65; }
    .pill { display:inline-block; background:#1a1f2e; border:1px solid #58a6ff55;
        border-radius:20px; padding:4px 14px; font-size:0.78rem; color:#58a6ff; margin-top:6px; }
    .stButton > button { background:linear-gradient(135deg,#238636,#2ea043);
        color:#fff; border:none; border-radius:7px; padding:10px 28px;
        font-weight:600; font-size:0.97rem; width:100%; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero">
        <h1>🔍 Code Review Feedback Generator</h1>
        <p>LangChain · Groq LLM · Langfuse Observability · Pydantic · Innomatics Research Labs</p>
    </div>""", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        st.markdown("**Model:** llama-3.1-8b-instant (Groq)")
        st.markdown("---")
        st.markdown("**Quality Levels**")
        for lvl, col in [("Excellent","#56d364"),("Good","#3fb950"),
                         ("Moderate","#d29922"),("Low","#f0883e"),("Critical","#f85149")]:
            st.markdown(f"<span style='color:{col}'>●</span> {lvl}", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("[🔗 Langfuse Dashboard](https://cloud.langfuse.com)")

    SAMPLES = {
        "Pick a sample": "",
        "Indentation Bug":   "for i in range(5):\nprint(i)",
        "No Error Handling": "def d(a,b): return a/b",
        "SQL Injection":     "def get(name):\n    import sqlite3\n    conn=sqlite3.connect('db.sqlite')\n    cur=conn.cursor()\n    cur.execute(\"SELECT * FROM users WHERE name='\"+name+\"'\")\n    return cur.fetchall()",
        "Clean Code":        "def fibonacci(n):\n    a,b,seq=0,1,[]\n    while len(seq)<n: seq.append(a);a,b=b,a+b\n    return seq",
        "Mutable Default":   "def append_to(e,to=[]):\n    to.append(e)\n    return to",
    }

    sample = st.selectbox("Load a sample", list(SAMPLES.keys()))
    code_input = st.text_area("Paste your code here:", value=SAMPLES[sample], height=200,
                               placeholder="# paste any code here...")

    if st.button("🔍 Review Code"):
        if not code_input.strip():
            st.warning("Please paste some code first.")
        else:
            session_id = f"ui-{uuid.uuid4().hex[:8]}"
            with st.spinner("Reviewing and sending trace to Langfuse..."):
                try:
                    result = review_code(code_input, session_id=session_id,
                                         trace_name="code-review-ui")
                    st.markdown("---")
                    st.markdown("## 📋 Results")
                    st.markdown(f'<div class="pill">🔗 Langfuse session: {session_id}</div>',
                                unsafe_allow_html=True)
                    level = result.code_quality_level.strip().title()
                    st.markdown(
                        f'<div class="card"><div class="card-title">Quality Level</div>'
                        f'<span class="badge q-{level}">{level}</span></div>',
                        unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        issues = "".join(f'<div class="issue">🔴 {i}</div>'
                                         for i in result.identified_issues) or '<div class="sug">✅ No issues!</div>'
                        st.markdown(
                            f'<div class="card"><div class="card-title">Issues ({len(result.identified_issues)})</div>{issues}</div>',
                            unsafe_allow_html=True)
                    with col2:
                        sugs = "".join(f'<div class="sug">💡 {s}</div>'
                                        for s in result.improvement_suggestions) or '<div class="sug">✅ Looks good!</div>'
                        st.markdown(
                            f'<div class="card"><div class="card-title">Suggestions ({len(result.improvement_suggestions)})</div>{sugs}</div>',
                            unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="card"><div class="card-title">Summary</div>'
                        f'<div class="summary">{result.review_summary}</div></div>',
                        unsafe_allow_html=True)
                    with st.expander("📄 Raw JSON"):
                        st.json(result.model_dump())
                except Exception as e:
                    st.error(f"Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--traces", action="store_true", help="Run 100 traces")
    parser.add_argument("--delay", type=float, default=0.3)
    args = parser.parse_args()
    if args.traces:
        run_100_traces(delay=args.delay)
    else:
        run_streamlit_ui()
else:
    run_streamlit_ui()