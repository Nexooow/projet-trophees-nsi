from src.utils.file import File

def test_file_basic():
    f = File()
    assert f.est_vide()
    f.enfiler("A")
    assert not f.est_vide()
    assert f.sommet() == "A"
    assert f.defiler() == "A"
    assert f.est_vide()

def test_file_priority():
    f = File()
    f.enfiler("A", priority=1)
    f.enfiler("B", priority=3)
    f.enfiler("C", priority=2)
    
    assert f.defiler() == "B"
    assert f.defiler() == "C"
    assert f.defiler() == "A"
    assert f.est_vide()

def test_file_init():
    f = File(["A", "B"])
    assert f.defiler() == "A"
    assert f.defiler() == "B"
    assert f.est_vide()
