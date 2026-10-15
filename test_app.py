import os,tempfile,unittest,io
os.environ['PLANNER_DB']=tempfile.mktemp(suffix='.sqlite3')
from fastapi.testclient import TestClient
from app import app,db
import openpyxl
class Flow(unittest.TestCase):
 def setUp(self):
  self.client=TestClient(app)
  with db() as c:
   for t in ['events','jobs','orders']:c.execute('DELETE FROM '+t)
 def seed(self):self.assertEqual(self.client.post('/api/demo').status_code,200);return self.client.get('/api/state').json()['orders'][0]
 def test_split_and_execution(self):
  o=self.seed();n=o['qty'];oid=o['id']
  a=self.client.post('/api/jobs',json=dict(order_id=oid,station='auto',qty=n-1)).json()['id']
  b=self.client.post('/api/jobs',json=dict(order_id=oid,station='stock',qty=1)).json()['id']
  self.assertEqual(self.client.post('/api/jobs',json=dict(order_id=oid,station='auto',qty=1)).status_code,409)
  self.assertEqual(self.client.post(f'/api/jobs/{a}/action',json={'action':'start'}).status_code,409)
  self.client.post('/api/publish');self.assertEqual(self.client.delete(f'/api/jobs/{a}').status_code,409)
  self.assertEqual(self.client.post(f'/api/jobs/{a}/action',json={'action':'start'}).status_code,200)
  self.assertEqual(self.client.post(f'/api/jobs/{a}/action',json={'action':'pause'}).status_code,400)
  self.client.post(f'/api/jobs/{a}/action',json={'action':'pause','note':'Brak etykiet'})
  self.client.post(f'/api/jobs/{a}/action',json={'action':'start'})
  self.assertEqual(self.client.post(f'/api/jobs/{a}/action',json={'action':'report','qty':n}).status_code,400)
  self.client.post(f'/api/jobs/{a}/action',json={'action':'report','qty':n-1})
  j=next(j for j in self.client.get('/api/state').json()['jobs'] if j['id']==a)
  self.assertEqual(j['state'],'done');self.assertEqual(j['done'],n-1)
 def test_station_exclusivity(self):
  o=self.seed();ids=[self.client.post('/api/jobs',json=dict(order_id=o['id'],station='auto',qty=1)).json()['id'] for _ in range(2)]
  self.client.post('/api/publish')
  self.client.post(f'/api/jobs/{ids[0]}/action',json={'action':'start'})
  self.assertEqual(self.client.post(f'/api/jobs/{ids[1]}/action',json={'action':'start'}).status_code,409)
 def test_import_and_duplicates(self):
  w=openpyxl.Workbook();s=w.active;s.append(['NAZWA KONTRAHENTA','NUMER ZAM.','NAZWA TOWARU','NAZWA RECEPTURY','ILOŚĆ','J.M.','KOD','OBJ.','LITRY','KOMENTARZ SPECJALNY']);s.append(['Klient','Z/1','Produkt','R1',10,'szt.','K','0,5',5,'uwaga']);f=io.BytesIO();w.save(f);raw=f.getvalue()
  self.assertEqual(self.client.post('/api/import',content=raw).json()['count'],1)
  self.assertEqual(self.client.post('/api/import',content=raw).status_code,409)
  s.cell(2,5,20);f=io.BytesIO();w.save(f)
  self.assertEqual(self.client.post('/api/import',content=f.getvalue()).status_code,409)
  self.assertEqual(len(self.client.get('/api/state').json()['orders']),1)
 def test_invalid_import_atomic(self):
  self.assertEqual(self.client.post('/api/import',content=b'bad').status_code,400)
  self.assertEqual(self.client.get('/api/state').json()['orders'],[])
if __name__=='__main__':unittest.main()
