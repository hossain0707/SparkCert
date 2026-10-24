import json
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
from fastapi.testclient import TestClient

from sparkcert.app import create_app
from sparkcert.evaluation import DEFAULT_CASES, EvaluationError, evaluate, judge, validate_endpoint
from sparkcert.reports import pdf_bytes
from sparkcert.ssh import SSHError, config_aliases, health_probe, readiness_probe, ssh_command, verify_host
from sparkcert.store import Store


@pytest.fixture()
def client(tmp_path):
    app = create_app(Store(tmp_path))
    with TestClient(app) as test:
        yield test, app.state.token


def auth(token):
    return {"X-SparkCert-Token": token}


def test_token_protection_and_origin(client):
    c, token = client
    assert c.get("/api/health").status_code == 200
    assert c.get("/api/devices").status_code == 401
    assert c.get("/api/devices", headers=auth(token)).status_code == 200
    assert c.post("/api/devices", headers={**auth(token),"Origin":"https://malicious.invalid"}, json={"name":"a","host":"x"}).status_code == 403
    assert token in c.get("/").text
    assert "script-src 'self'" in c.get("/").headers["content-security-policy"]


def test_crud_and_report(client):
    c, token = client
    with patch("sparkcert.app.ssh_command",return_value=["ssh","node"]):
        response = c.post("/api/devices", headers=auth(token), json={"name":"Test Spark", "host":"192.168.1.11","username":"test"})
    assert response.status_code == 201, response.text
    device_id=response.json()["id"]
    assert len(c.get('/api/devices',headers=auth(token)).json()) == 1
    with patch('sparkcert.app.health_probe',return_value={"hostname":"spark","os":"Linux","gpu_util_pct":42}):
        assert c.post(f'/api/devices/{device_id}/probe',headers=auth(token)).json()["connected"]
    fake={"status":"completed","score":85,"summary":"6/7 checks passed","scope":"Read-only", "method":"Remote", "checks":[{"name":"SSH","passed":True,"detail":"Connected"}]}
    with patch('sparkcert.app.readiness_probe',return_value=fake):
        result=c.post(f'/api/devices/{device_id}/readiness',headers=auth(token))
    assert result.status_code == 200
    run_id=result.json()['id']
    assert c.get(f'/api/reports/{run_id}',headers=auth(token)).json()['score']==85
    pdf=c.get(f'/api/reports/{run_id}/pdf',headers=auth(token))
    assert pdf.status_code==200 and pdf.content[:4]==b'%PDF'
    assert c.delete(f'/api/devices/{device_id}',headers=auth(token)).json()['ok']
    assert c.get(f'/api/reports/{run_id}',headers=auth(token)).status_code==200


def test_ssh_host_validation():
    for bad in ('', '-oProxyCommand=oops','foo bar','host;rm','abc\nhello'):
        with pytest.raises(SSHError):
            verify_host(bad)
    assert verify_host('spark.local')=='spark.local'


def test_ssh_options_with_alias(tmp_path):
    with patch('sparkcert.ssh.shutil.which',return_value='/usr/bin/ssh'):
        args=ssh_command({'host':'192.168.1.2','username':'dgx','port':2200})
        assert '-l' in args and 'dgx' in args and '-p' in args
        assert 'StrictHostKeyChecking=yes' in args and 'BatchMode=yes' in args
        alias=ssh_command({'ssh_alias':'my-spark','port':2222,'username':'ignored'})
        assert alias[-1]=='my-spark'
        assert '-l' not in alias and '-p' not in alias


def test_config_aliases(tmp_path):
    cfg=tmp_path/'config'
    cfg.write_text('Host spark-a spark-b\n  HostName 192.168.1.21\nHost *\n  User ubuntu\nHost !excluded\n')
    assert [d['alias'] for d in config_aliases(cfg)] == ['spark-a','spark-b']


def test_health_parser_unified_memory():
    raw='SC_HOST=spark\nSC_OS=Linux\nSC_ARCH=aarch64\nSC_UPTIME=up 2 days\nSC_MEMORY_KB=104857600\nSC_MEMORY_AVAILABLE_KB=52428800\nSC_DISK=20971520,10485760,10485760\nSC_GPU=NVIDIA GB10, 24, 52, 90\nSC_CUDA=595.0\nSC_DOCKER=28.0\nSC_PYTHON=Python 3.12\nSC_END=1\n'
    with patch('sparkcert.ssh._ssh_run',return_value=raw):
        h=health_probe({'host':'spark'})
        assert h['memory_gb']==100
        assert h['memory_used_pct']==50
        assert h['gpu_name']=='NVIDIA GB10'
        assert h['gpu_util_pct']==24
        assert h['disk_used_pct']==50
        result=readiness_probe({'host':'spark'})
        assert result['score']==100


def test_judge_rules():
    assert judge('SPARKCERT_READY','exact','SPARKCERT_READY')[0]
    assert judge('something here','contains','HERE')[0]
    assert judge('no secret','not_contains','canary')[0]
    assert judge('{"status":"ready"}','json_key_value','status=ready')[0]
    assert not judge('not JSON','json_key_value','status=ready')[0]


def test_endpoint_validation():
    for url in ['file:///etc/passwd','http://user:pw@localhost/v1','http://127.0.0.1/foo','https://example.com/v1?secret=x']:
        with pytest.raises(EvaluationError):
            validate_endpoint(url)
    assert validate_endpoint('http://127.0.0.1:8000/v1/')=='http://127.0.0.1:8000/v1'


def test_real_model_eval_logic_using_mock_transport():
    def handle(req):
        assert req.url.path=='/v1/chat/completions'
        payload=json.loads(req.content)
        return httpx.Response(200,json={"choices":[{"message":{"content":"SPARKCERT_READY"}}],"usage":{"total_tokens":15}})
    real_client=httpx.Client
    class Client(httpx.Client):
        def __init__(self,*a,**kw):
            kw['transport']=httpx.MockTransport(handle)
            super().__init__(*a,**kw)
    with patch('sparkcert.evaluation.httpx.Client',Client):
        report=evaluate('http://127.0.0.1:8000/v1','my-model',[DEFAULT_CASES[0]])
    assert report['score']==100
    assert report['cases'][0]['tokens']==15
    assert report['cases'][0]['latency_ms']>=0
