import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from modules import seed, dataset_validator as dv, evidence_extraction as ee, question_generator as qg
from modules.question_validator import validate_question, parse_json
M, Q, P = seed.materials(), seed.questions(), seed.mapping()
def test_valid(): assert dv.validate_materials(M)[0]["status"] == "Valid" and dv.validate_questions(Q)[0]["status"] == "Valid" and dv.validate_mapping(P, M.materi_id, Q["Kode Soal"])[0]["status"] == "Valid"
def test_bad_key():
    q = Q.copy(); q.loc[0, "Kunci Jawaban"] = "b"; assert dv.validate_questions(q)[0]["error"] >= 1
def test_retrieval(): assert ee.retrieve(M, "ide pokok paragraf", "Ide Pokok").topik.eq("Ide Pokok").all()
def test_demo_generation():
    ev = ee.retrieve(M, "fakta opini", "Fakta dan Opini", k=3); s, qs, _, _ = qg.generate(ev, None, 3, "Fakta dan Opini", "x", "Sedang", "x", "OpenAI", "m", True)
    assert s == "success" and len(qs) == 3 and all(not validate_question(x, set(ev.materi_id)) for x in qs) and len(qg.to_22(qs[0])) == 22
def test_json(): assert parse_json('```json\n{"a":1}\n```') == {"a": 1}
