#!/usr/bin/env python3
import json,sys
from pathlib import Path

def audit(path,out):
    x=json.loads(Path(path).read_text(encoding='utf-8'))
    errors=[]; warnings=[]
    if x.get('version')!='V2': errors.append('version_incorrecta')
    if x.get('interpretacion') is not False: errors.append('interpretacion_no_bloqueada')
    if x.get('fractalidad_declarada') is not False: errors.append('fractalidad_declarada')
    for p in x.get('resultados',[]):
        if p.get('estado')=='RELACION_MULTIESCALA' and p.get('numero_escalas',0)<2: errors.append(f'multiescala_sin_2_escalas:{p.get("id_relacion")}')
        if p.get('es_fractal') is not False: errors.append(f'fractalidad_en_patron:{p.get("id_relacion")}')
    if x.get('familias_multiescala_candidatas',0): warnings.append('familias_multiescala_requieren_validacion_semantica')
    result={'version':'V2','estado':'AUDITORIA_OK' if not errors else 'AUDITORIA_ERROR','errores':errors,'advertencias':warnings,'registros_fuente':x.get('registros_fuente'), 'detecciones':x.get('detecciones'),'patrones':x.get('patrones'),'familias_multiescala_candidatas':x.get('familias_multiescala_candidatas',0),'regla_minima_escalas':2,'interpretacion_permitida':False,'fractalidad_permitida':False}
    Path(out).parent.mkdir(parents=True,exist_ok=True); Path(out).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if not errors else 1

if __name__=='__main__':
    if len(sys.argv)!=3: raise SystemExit('Uso: python ALACRAN_V2_AUDIT.py <resultado.json> <auditoria.json>')
    raise SystemExit(audit(*sys.argv[1:]))
